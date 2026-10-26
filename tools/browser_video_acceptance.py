"""Browser acceptance of the real player with an explicit synthetic media sample.

No model, canonical voice, owner credentials, episode selection or publication.
All browser requests are intercepted; the MP4 exists only to test decoding/seeking.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit
import zipfile


def run(out):
    from playwright.sync_api import sync_playwright
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fdg-player-') as directory:
        movie = Path(directory) / 'sample.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
            'testsrc2=size=640x360:rate=12:duration=6', '-f', 'lavfi', '-i',
            'sine=frequency=880:sample_rate=48000:duration=6', '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(movie)],
            check=True, timeout=30)
        media = movie.read_bytes()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('EPISODIO_PARA_REVISION.mp4', media)
        package = buffer.getvalue()
    digest = lambda data: hashlib.sha256(data).hexdigest()
    video_id = digest(media)
    root = Path(__file__).resolve().parents[1]
    flags = {'expired': False}
    calls = []
    token = 'local-browser-fixture-no-owner-credential'
    html = '''<!doctype html><html lang="es"><title>Prueba del reproductor · sin episodio</title>
      <h1>Prueba técnica de reproducción, audio y desplazamiento</h1><div id="player"></div>
      <script type="module">
      import {mountVideoPreview} from '/video-preview.js';
      window.revoked=[];
      window.mount=()=>window.dispose=mountVideoPreview(document.querySelector('#player'),
        {id:VIDEO_ID,title:'Muestra sintética de seis segundos'}, {
         fetchArchive:(url,options)=>fetch(url,{...options,headers:{Authorization:'Bearer TOKEN'}}),
         urlApi:{createObjectURL:blob=>URL.createObjectURL(blob),
          revokeObjectURL:url=>{window.revoked.push(url);URL.revokeObjectURL(url);}}
        });
      window.mount();window.ready=true;
      </script></html>'''.replace('VIDEO_ID', json.dumps(video_id)).replace('TOKEN', token)
    with sync_playwright() as playwright:
        executable = next((shutil.which(name) for name in ('google-chrome', 'chromium', 'chromium-browser')
                           if shutil.which(name)), None)
        browser = playwright.chromium.launch(headless=True, executable_path=executable,
            args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page()
        page.set_default_timeout(15000)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))

        def intercept(route):
            request = route.request
            parsed = urlsplit(request.url)
            if parsed.hostname != 'factor.test':
                errors.append('Unexpected external browser request: ' + parsed.hostname)
                return route.abort()
            if parsed.path == '/':
                return route.fulfill(content_type='text/html', body=html)
            if parsed.path == '/video-preview.js':
                return route.fulfill(content_type='text/javascript', body=(root / 'public/video-preview.js').read_text())
            if parsed.path == '/api/youtube/exports/' + video_id + '/preview':
                calls.append(request.headers.get('authorization'))
                if request.headers.get('authorization') != 'Bearer ' + token:
                    return route.fulfill(status=401, json={'error': 'Acceso no autorizado'})
                if flags['expired']:
                    return route.fulfill(status=410, json={'error': 'El archivo de revisión ha caducado.'})
                return route.fulfill(content_type='application/zip', body=package, headers={
                    'X-Archive-Bytes': str(len(package)), 'X-Archive-SHA256': digest(package),
                    'X-Video-Bytes': str(len(media)), 'X-Video-SHA256': video_id})
            return route.fulfill(status=404)

        page.route('**/*', intercept)
        try:
            page.goto('https://factor.test/')
            page.wait_for_function('window.ready===true')
            assert page.evaluate("async id=>(await fetch('/api/youtube/exports/'+id+'/preview')).status", video_id) == 401
            page.get_by_role('button', name='Ver video en el panel').click()
            page.wait_for_function('document.querySelector("video").readyState>=2')
            measured = page.evaluate('''async()=>{
              const v=document.querySelector('video');
              const context=new AudioContext(),analyser=context.createAnalyser();
              context.createMediaElementSource(v).connect(analyser);analyser.connect(context.destination);
              await context.resume();await v.play();
              let peak=0;const values=new Float32Array(analyser.fftSize);
              const until=performance.now()+600;
              while(performance.now()<until){
                analyser.getFloatTimeDomainData(values);
                peak=Math.max(peak,Math.sqrt(values.reduce((s,x)=>s+x*x,0)/values.length));
                await new Promise(r=>setTimeout(r,20));
              }
              const advanced=v.currentTime;v.pause();
              const sought=new Promise(resolve=>v.addEventListener('seeked',resolve,{once:true}));
              v.currentTime=4;await sought;
              const result={duration:v.duration,width:v.videoWidth,height:v.videoHeight,
                audio_rms:peak,advanced,paused:v.paused,seeked:v.currentTime,controls:v.controls};
              await context.close();return result;
            }''')
            assert measured['duration'] >= 5.9 and measured['width'] == 640 and measured['height'] == 360, measured
            assert measured['advanced'] > .1 and measured['audio_rms'] > .001, measured
            assert measured['paused'] and measured['controls'] and abs(measured['seeked'] - 4) < .1, measured
            page.screenshot(path=str(out / 'REPRODUCTOR.png'))
            page.evaluate("document.querySelector('video').dispatchEvent(new Event('error'))")
            page.get_by_role('button', name='Volver a preparar el video').click()
            page.wait_for_function('window.revoked.length===1 && document.querySelector("video").readyState>=2')
            page.evaluate('window.dispose();document.querySelector("#player").replaceChildren();window.mount()')
            flags['expired'] = True
            page.get_by_role('button', name='Ver video en el panel').click()
            page.get_by_role('status').filter(has_text='caducado').wait_for()
            assert page.locator('video').get_attribute('src') is None
            assert page.get_by_role('button').is_enabled()
            flags['expired'] = False
            page.get_by_role('button').click()
            page.wait_for_function('document.querySelector("video").readyState>=2')
            page.evaluate('window.dispose()')
            assert page.evaluate('window.revoked.length') == 3
            assert not errors, errors
            report = {'browser': browser.version, 'real_mp4_decoded': True, **measured,
                'authentication_enforced': True, 'expiry_visible': True, 'retry_without_render': True,
                'blob_cleanup_verified': True, 'provider_calls': 0, 'sample_kind': 'synthetic_test_only',
                'production_episode_accepted': False}
            (out / 'ACEPTACION_REPRODUCTOR.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            print('REPRODUCTOR_VERIFICADO:', json.dumps(report, ensure_ascii=False))
            return report
        finally:
            browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('dist/browser-acceptance'))
    run(parser.parse_args().out)
