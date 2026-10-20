#!/usr/bin/env python3
"""Produce a technically reproducible preview: original slides + local Spanish speech.
No upload to YouTube. No remote media downloaded. This is not monetization-quality output.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

# Render audiovisual 0.2: módulos propios sin peticiones externas de IA.
if __package__:
    from .voice import MODEL_NAME, synthesize, credits
    from .subtitles import make_srt
else:
    from voice import MODEL_NAME, synthesize, credits
    from subtitles import make_srt
import urllib.error
import urllib.parse


def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError("Manifest debe ser objeto")
    title = data.get("title")
    angle = data.get("angle")
    if not isinstance(title, str) or not 8 <= len(title.strip()) <= 150:
        raise ValueError("Título inválido")
    if not isinstance(angle, str) or not 15 <= len(angle.strip()) <= 700:
        raise ValueError("Enfoque inválido")
    if data.get("format") not in ("short", "long"):
        raise ValueError("Formato inválido")
    sources = data.get("sources")
    if not isinstance(sources, list) or not 2 <= len(sources) <= 20 or not all(
        isinstance(s, str) and s.startswith("https://") for s in sources
    ):
        raise ValueError("Se requieren fuentes https verificadas por el editor")
    segments = data.get("segments")
    if not isinstance(segments, list) or not 2 <= len(segments) <= 18:
        raise ValueError("Se requieren 2-18 segmentos")
    for s in segments:
        if not isinstance(s, dict) or not isinstance(s.get("headline"), str) or not isinstance(s.get("voiceover"), str):
            raise ValueError("Segmento incompleto")
        if not 1 <= len(s["headline"].strip()) <= 110 or not 15 <= len(s["voiceover"].strip()) <= 900:
            raise ValueError("Longitud de segmento inválida")
    return data


def command(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def duration(wav):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(wav)],
        check=True, text=True, capture_output=True
    )
    return float(result.stdout.strip())


def wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def slide(path, title, headline, excerpt, index, count, fmt):
    from PIL import Image, ImageDraw, ImageFont

    width, height = (720, 1280) if fmt == "short" else (1280, 720)
    image = Image.new("RGB", (width, height), "#111318")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        shade = int(17 + 16 * y / height)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 1, shade + 5))
    # Original abstract brand graphics, not misleading footage of real events.
    cx, cy = int(width * .80), int(height * .32)
    for n in range(7):
        radius = int((min(width, height) * .23) + n * 16)
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius),
                     outline=(82 + n * 5, 61 + n * 4, 31 + n * 3), width=2)
    baseline = int(height * .80)
    for i in range(9):
        x = int(width * (.65 + i * .035))
        top = baseline - (i * 31 + (i % 3) * 45)
        draw.rectangle((x, top, x + 13, baseline), fill=(135 + i * 8, 101 + i * 8, 48 + i * 4))
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not Path(font_path).exists():
        raise FileNotFoundError("Se requiere instalar fonts-dejavu-core")
    small = ImageFont.truetype(bold_path, 20 if fmt == "short" else 19)
    head = ImageFont.truetype(bold_path, 43 if fmt == "short" else 60)
    body = ImageFont.truetype(font_path, 24 if fmt == "short" else 27)
    brand = ImageFont.truetype(bold_path, 25 if fmt == "short" else 26)
    margin = 53 if fmt == "short" else 78
    draw.text((margin, margin), "FACTOR DE GIGANTES", fill="#efc87e", font=brand)
    draw.text((margin, margin + 50), "DOCUMENTAL · PRUEBA", fill="#d7d9db", font=small)
    if fmt == "short":
        top = int(height * .25)
    else:
        top = int(height * .29)
    headline_lines = wrap(draw, headline.upper(), head, width - 2 * margin)
    if len(headline_lines) > 4:
        raise ValueError("Título demasiado largo para tarjeta")
    for line in headline_lines:
        draw.text((margin, top), line, fill="#f5e9d7", font=head)
        top += (65 if fmt == "short" else 80)
    top += 24
    excerpt = re.sub(r"\s+", " ", excerpt)[:210]
    max_lines = 5 if fmt == "short" else 3
    for line in wrap(draw, excerpt, body, width - 2 * margin)[:max_lines]:
        draw.text((margin, top), line, fill="#d6d3ce", font=body)
        top += 40
    draw.line((margin, height - 100, width-margin, height-100), fill="#bd9142", width=3)
    draw.text((margin, height - 76), f"ESCENA {index:02d} / {count:02d}  •  PRODUCCIÓN DE PRUEBA", fill="#d6ba85", font=small)
    image.save(path)



def _video_info(path, fmt):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height:format=duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    data = json.loads(result.stdout)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    size = (720, 1280) if fmt == "short" else (1280, 720)
    if not video or not audio or (video.get("width"), video.get("height")) != size:
        raise RuntimeError("Archivo no válido: requiere video, audio y resolución correcta")
    length = float(data["format"]["duration"])
    if length < 2 or path.stat().st_size < 15000:
        raise RuntimeError("Video vacío o incompleto")
    return {"duration_seconds": round(length, 2), "width": size[0], "height": size[1],
            "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name"),
            "bytes": path.stat().st_size}


def _motion_clip(scene, audio, clip, length, fmt):
    size = "720x1280" if fmt == "short" else "1280x720"
    zoom = ("zoompan=z='min(zoom+0.00019,1.075)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s={size}:fps=24")
    filters = f"[0:v]{zoom},fade=t=in:st=0:d=0.28[v];[1:a]apad=pad_dur=0.35[a]"
    command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-framerate", "24", "-i", str(scene),
            "-i", str(audio), "-filter_complex", filters,
            "-map", "[v]", "-map", "[a]", "-t", f"{length:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            "-r", "24", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(clip))


def _burn_subtitles(input_file, subtitle_file, output_file, fmt):
    # Directorio temporal propio, ruta controlada sin caracteres de FFmpeg peligrosos.
    if not re.fullmatch(r"[\w/.\-]+", str(subtitle_file)):
        raise ValueError("Ruta de subtítulos incompatible con FFmpeg")
    fontsize, bottom = (19, 150) if fmt == "short" else (22, 43)
    style = (f"FontName=DejaVu Sans,FontSize={fontsize},"
             "PrimaryColour=&H00FFFFFF,OutlineColour=&H00111111,"
             f"Outline=2,Shadow=1,Alignment=2,MarginV={bottom}")
    vf = f"subtitles=filename={subtitle_file}:force_style='{style}'"
    command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(input_file), "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
            str(output_file))


def render(manifest, output, voice_engine="espeak", captions="burn",
           cache_dir="~/.cache/factor-de-gigantes/voices"):
    """Escenas originales, voz local elegida, Ken Burns, SRT y QA final."""
    validate_manifest(manifest)
    if voice_engine not in ("piper", "espeak"):
        raise ValueError("Motor de voz inválido")
    if captions not in ("burn", "sidecar"):
        raise ValueError("Formato de subtítulos inválido")
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="factor-video-") as tmp:
        root = Path(tmp)
        clips, times = [], []
        total = 0.0
        for i, segment in enumerate(manifest["segments"], 1):
            audio = root / f"voice-{i:02}.wav"
            scene = root / f"slide-{i:02}.png"
            clip = root / f"clip-{i:02}.mp4"
            # No fallback silencioso. La ejecución falla si Piper no está disponible.
            synthesize(segment["voiceover"], audio, voice_engine, cache_dir)
            length = duration(audio) + 0.24
            total += length
            if manifest["format"] == "short" and total > 180:
                raise ValueError("Short supera 180 segundos; dividir o reducir guion")
            slide(scene, manifest["title"], segment["headline"], segment["voiceover"], i,
                  len(manifest["segments"]), manifest["format"])
            _motion_clip(scene, audio, clip, length, manifest["format"])
            clips.append(clip)
            times.append(duration(clip))
            print(f"Escena {i}/{len(manifest['segments'])}: {times[-1]:.1f} s", flush=True)
        playlist = root / "concat.txt"
        playlist.write_text("".join(f"file '{p.name}'\n" for p in clips), encoding="utf-8")
        merged = root / "montaje.mp4"
        command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(playlist),
                "-c", "copy", "-movflags", "+faststart", str(merged))
        subpath = output.parent / "subtitulos.srt"
        subpath.write_text(make_srt(manifest["segments"], times), encoding="utf-8")
        if captions == "burn":
            _burn_subtitles(merged, subpath, output, manifest["format"])
        else:
            output.write_bytes(merged.read_bytes())
    info = _video_info(output, manifest["format"])
    (output.parent / "creditos.txt").write_text(
        "FACTOR DE GIGANTES - PREVISUALIZACION TECNICA. NO PUBLICAR.\n"
        "Graficos abstractos: originales, no metraje historico real.\n"
        "Subtitulos: tiempos estimados desde el audio, no alineacion fonetica.\n"
        + credits(voice_engine), encoding="utf-8")
    metadata = {
        "schema_version": 1, "brand": "Factor de Gigantes", "render": "preview",
        "approved_script_title": manifest["title"], "format": manifest["format"],
        "voice_engine": voice_engine,
        "voice_model": MODEL_NAME if voice_engine == "piper" else "espeak-es",
        "caption_style": captions, "caption_alignment": "estimated",
        "source_urls": manifest["sources"], "sources_fact_checked": False,
        "visuals": "original abstract editorial graphics; NOT archival footage",
        "distribution": "preview_only_not_uploaded_to_youtube",
        "technical_quality": info
    }
    (output.parent / "ficha.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Video producido: {output} ({info['duration_seconds']}s, {info['bytes']} bytes)")
    return metadata


def remote_manifest(job_id):
    base = os.environ.get("API_BASE_URL", "").rstrip("/")
    token = os.environ.get("RENDERER_TOKEN", "")
    if not base.startswith("https://") or len(token) < 24:
        raise RuntimeError("Configura secretos API_BASE_URL (HTTPS) y RENDERER_TOKEN")
    if not re.fullmatch(r"[0-9a-f-]{36}", job_id):
        raise ValueError("job_id inválido")
    # Diagnóstico seguro: muestra solamente el host público, nunca los tokens.
    host = urllib.parse.urlsplit(base).hostname or ""
    print("Destino del motor:", host, flush=True)
    headers = {"User-Agent": "FactorDeGigantes-Renderer/1.0", "Accept": "application/json"}
    health_req = urllib.request.Request(base + "/health", headers=headers)
    try:
        with urllib.request.urlopen(health_req, timeout=30) as response:
            health = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"El servicio configurado en API_BASE_URL rechaza /health (HTTP {exc.code}). "
            "Comprueba que API_BASE_URL sea la URL HTTPS exacta del Worker; "
            "si el dominio es correcto, revisa bloqueos de Cloudflare."
        ) from None
    if health.get("ok") is not True or health.get("product") != "Factor de Gigantes":
        raise RuntimeError("API_BASE_URL no apunta al Worker Factor de Gigantes esperado")
    print("Conexión /health confirmada", flush=True)
    url = base + "/api/renderer/jobs/" + job_id
    req = urllib.request.Request(url, headers={**headers, "Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)["manifest"]
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise RuntimeError(
                "El Worker rechazó RENDERER_TOKEN (HTTP 401): "
                "comprobar que coincide en Cloudflare y GitHub Actions."
            ) from None
        if exc.code == 403:
            raise RuntimeError(
                "La consulta autenticada recibió HTTP 403; "
                "comprobar protección y reglas de Cloudflare."
            ) from None
        raise RuntimeError(f"Error al consultar el guion: HTTP {exc.code}") from None


def main():
    parser = argparse.ArgumentParser(description="Motor preliminar Factor de Gigantes")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--manifest", help="Archivo JSON local")
    src.add_argument("--remote", action="store_true", help="Leer trabajo aprobado del Worker")
    parser.add_argument("--job-id", default="", help="UUID aprobado, solo en modo --remote")
    parser.add_argument("--output", default="dist/video.mp4")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--voice-engine", choices=("piper", "espeak"), default="espeak")
    parser.add_argument("--captions", choices=("burn", "sidecar"), default="burn")
    parser.add_argument("--voice-cache", default="~/.cache/factor-de-gigantes/voices")
    args = parser.parse_args()
    if args.remote and not args.job_id:
        parser.error("--remote requiere --job-id")
    content = remote_manifest(args.job_id) if args.remote else json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    validate_manifest(content)
    if args.validate_only:
        print("Manifest validado")
    else:
        render(content, args.output, args.voice_engine, args.captions, args.voice_cache)


if __name__ == "__main__":
    main()
