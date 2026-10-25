"""Contrato común de producción: investigación de desarrollo o guion autónomo.

Los fixtures preparados por Codex no acreditan que una IA externa investigó.
Ningún paquete concede derechos, aprobación humana ni publicación.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
from tools.research_engine import validate_url

from tools.approved_voice import SHA
from tools.documentary_production_plan import segment_text

VISUAL_KINDS = {'process', 'network', 'comparison', 'timeline', 'document', 'verdict'}
WORDS = re.compile(r'\b\w+\b', re.UNICODE)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def text(value, minimum, maximum):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum or '\x00' in value:
        raise ValueError('Texto del paquete fuera de contrato')
    return value


def validate_episode(episode):
    if not isinstance(episode, dict) or episode.get('schema') != 'fdg_episode_package_v1':
        raise ValueError('Paquete de episodio no reconocido')
    if episode.get('origin') not in ('codex_development_research', 'autonomous_script'):
        raise ValueError('Procedencia del paquete requerida')
    for flag in ('publication_authorized', 'human_factual_approval', 'commercial_rights_verified'):
        if episode.get(flag) is not False:
            raise ValueError('Este paquete no concede permisos editoriales ni comerciales')
    if episode.get('canonical_voice_sha256') != SHA:
        raise ValueError('La identidad del narrador debe ser la canónica')
    text(episode.get('title'), 10, 150)
    text(episode.get('company'), 3, 130)
    text(episode.get('central_question'), 25, 500)
    sources = episode.get('sources')
    if not isinstance(sources, list) or not 2 <= len(sources) <= 30:
        raise ValueError('Fuentes documentales requeridas')
    by_id = {}
    for source in sources:
        sid = source.get('id')
        if not isinstance(sid, str) or not re.fullmatch(r'S\d{2}', sid) or sid in by_id:
            raise ValueError('Identidad de fuente inválida')
        validate_url(source.get('url', ''))
        u = urlsplit(source.get('url', ''))
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.port or \
                u.hostname in ('localhost', '0.0.0.0', '::1') or re.match(r'^(127|10|192\.168|169\.254)\.', u.hostname):
            raise ValueError('Fuente requiere URL HTTPS pública')
        text(source.get('title'), 5, 250)
        text(source.get('publisher'), 3, 130)
        text(source.get('locator'), 4, 700)
        by_id[sid] = source
    def references(ids):
        if not isinstance(ids, list) or not 1 <= len(ids) <= 10 or len(set(ids)) != len(ids) or \
                any(sid not in by_id for sid in ids):
            raise ValueError('Contenido sin fuentes existentes')
    scenes = episode.get('scenes')
    if not isinstance(scenes, list) or not 6 <= len(scenes) <= 12:
        raise ValueError('Documental requiere entre seis y doce escenas')
    words = 0
    for number, scene in enumerate(scenes, 1):
        if scene.get('id') != f'SC{number:02d}':
            raise ValueError('Orden de escenas inválido')
        text(scene.get('headline'), 5, 100)
        paragraphs = scene.get('paragraphs')
        if not isinstance(paragraphs, list) or not 1 <= len(paragraphs) <= 8:
            raise ValueError('Escena sin párrafos documentados')
        for p in paragraphs:
            words += len(WORDS.findall(text(p.get('text'), 40, 3500)))
            references(p.get('source_ids'))
        visual = scene.get('visual', {})
        if visual.get('kind') not in VISUAL_KINDS:
            raise ValueError('Tipo de visual no soportado')
        items = visual.get('items')
        if not isinstance(items, list) or not 2 <= len(items) <= 6:
            raise ValueError('Cada visual requiere datos propios de la escena')
        for item in items:
            text(item.get('label'), 2, 75)
            references(item.get('source_ids'))
            if 'value' in item and (type(item['value']) not in (int, float) or
                                   not math.isfinite(item['value']) or not 0 <= item['value'] <= 1e12):
                raise ValueError('Dato visual numérico inválido')
        if visual['kind'] == 'comparison' and any('value' not in x for x in items):
            raise ValueError('Comparación sin cantidades documentadas')
    seconds = math.ceil(words * 60 / 138)
    if not 480 <= seconds <= 840:
        raise ValueError('El texto debe alcanzar ocho a catorce minutos estimados')
    return {'episode_sha256': digest(episode), 'narration_words': words,
            'estimated_seconds': seconds, 'scene_count': len(scenes), 'source_count': len(sources)}


def voice_plan(episode):
    summary = validate_episode(episode)
    tasks = []
    for scene in episode['scenes']:
        for n, p in enumerate(scene['paragraphs'], 1):
            for part, (begin, end, narration) in enumerate(segment_text(p['text']), 1):
                tasks.append({'id': f"{scene['id']}_P{n:02d}_T{part:02d}", 'scene_id': scene['id'],
                              'paragraph_index': n, 'text': narration, 'character_start': begin,
                              'character_end': end, 'text_sha256': hashlib.sha256(narration.encode()).hexdigest(),
                              'source_ids': p['source_ids']})
    if len(tasks) > 128:
        raise ValueError('Presupuesto máximo de 128 tomas')
    return {'schema': 'fdg_episode_voice_plan_v1', **summary, 'tasks': tasks,
            'canonical_voice_sha256': SHA, 'publication_authorized': False}


def from_autonomous(script, research):
    """Adaptar el mismo borrador citado; no editar D1 ni saltar la puerta del guionista."""
    from tools.documentary_blueprint import inspect_episode
    from tools.documentary_production_plan import prepare_production
    from tools.documentary_script import parse_script
    from tools.script_provenance import evidence_link_sha256
    selection = {'selected_wikidata_id': research['selected_wikidata_id'],
                 'research_queue': {'wikidata_id': research['selected_wikidata_id'], 'title': research['company']}}
    blueprint=inspect_episode(research, selection)
    if blueprint['status'] != 'source_grounded_outline_unapproved' or \
            script.get('source_evidence_sha256') != evidence_link_sha256(research) or \
            script.get('wikidata_id') != research['selected_wikidata_id']:
        raise ValueError('No adaptar investigación bloqueada o guion ajeno')
    prepare_production(script)
    parse_script(json.dumps({'title':script['title'],'central_question':script['central_question'],
        'scenes':[{'scene_number':s['scene_number'],'paragraphs':s['paragraphs']} for s in script['scenes']]},
        ensure_ascii=False),research,blueprint)
    evidence = {e['id']: e for e in research['evidence_manifest']}
    urls = list(dict.fromkeys(e['url'] for e in evidence.values()))
    ids = {url:f'S{n:02d}' for n,url in enumerate(urls, 1)}
    scenes = []
    for n, source in enumerate(script['scenes'], 1):
        paragraphs = [{'text': p['text'], 'source_ids': list(dict.fromkeys(
            ids[evidence[key]['url']] for key in p['evidence_ids']))} for p in source['paragraphs']]
        refs = list(dict.fromkeys(key for p in paragraphs for key in p['source_ids']))
        scenes.append({'id': f'SC{n:02d}', 'headline': f"{script['company'][:75]} · Escena {n}",
            'paragraphs': paragraphs, 'visual': {'kind': 'document', 'items': [
                {'label': 'Afirmación documental', 'source_ids': refs},
                {'label': 'Contraste y contexto', 'source_ids': refs}]}})
    out = {'schema': 'fdg_episode_package_v1', 'origin': 'autonomous_script',
           'title': script['title'], 'company': script['company'], 'central_question': script['central_question'],
           'canonical_voice_sha256': SHA, 'publication_authorized': False,
           'human_factual_approval': False, 'commercial_rights_verified': False,
           'sources': [{'id': ids[url], 'url': url, 'title': 'Documento del expediente '+ids[url],
                        'publisher': urlsplit(url).hostname, 'locator': 'Pasajes '+', '.join(
                            e['id'] for e in evidence.values() if e['url']==url)} for url in urls], 'scenes': scenes}
    validate_episode(out)
    return out


def write_manuscript(episode, destination):
    summary = validate_episode(episode)
    lines = [f"# {episode['title']}", '', '**Borrador de desarrollo — sin aprobación comercial/publicación**', '',
             f"Procedencia: {episode['origin']}. {summary['narration_words']} palabras; "
             f"{summary['estimated_seconds']} segundos estimados a 138 palabras/minuto.", '', episode['central_question'], '']
    for scene in episode['scenes']:
        lines += [f"## {scene['id']} · {scene['headline']}", '']
        for p in scene['paragraphs']:
            lines += [p['text'], '', 'Fuentes: '+', '.join(p['source_ids'])+'.', '']
    lines += ['## Fuentes consultadas', '']
    for source in episode['sources']:
        lines += [f"- {source['id']}: [{source['title']}]({source['url']}). {source['locator']}"]
    Path(destination).write_text('\n'.join(lines)+'\n', encoding='utf-8')
