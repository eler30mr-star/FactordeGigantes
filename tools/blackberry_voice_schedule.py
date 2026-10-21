"""Plan de lotes de voz para las 12 escenas BlackBerry. Solo planificación.

No ejecuta Qwen, no produce audio ni video, no autoriza licencias/publicación.
Conserva todas las palabras del manuscrito y obliga a lotes CPU por escena.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from tools.blackberry_script_quality import DEFAULT_SCRIPT,HEADER

LOW=120
HIGH=260
IDEAL=211
MAX_SCENES=12
MAX_CLIPS_PER_SCENE=8
MAX_BATCH_CHARS=2100
SENTENCE_BREAK=re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿])")
CLAUSE_BREAK=re.compile(r"(?<=,)\s+")


def all_scene_voices(text):
    matches=list(HEADER.finditer(text))
    if len(matches)!=12:
        raise ValueError("Se requieren 12 escenas originales")
    voices=[]
    for i,match in enumerate(matches):
        endpoint=matches[i+1].start() if i+1<len(matches) else text.find("\n---",match.end())
        if endpoint<0:
            endpoint=len(text)
        match_voice=re.search(
            r"\*\*NARRADOR\*\*\s*(.*?)\s*\*\*FUENTES POR COMPROBAR:\*\*",
            text[match.end():endpoint],re.S
        )
        if not match_voice:
            raise ValueError(f"Escena {i+1} sin narrador")
        voice=" ".join(match_voice.group(1).split())
        voices.append((i+1,match.group(2),voice))
    return voices


def partition(phrases,min_length=LOW,max_length=HIGH):
    # Programación dinámica, divisiones entre oraciones y cláusulas; nunca elimina palabras.
    dp=[None]*(len(phrases)+1)
    dp[-1]=(0,[])
    for start in range(len(phrases)-1,-1,-1):
        for stop in range(start+1,len(phrases)+1):
            part=" ".join(phrases[start:stop])
            if len(part)>max_length:
                break
            if len(part)<min_length or dp[stop] is None:
                continue
            cost=abs(len(part)-IDEAL)+dp[stop][0]
            if dp[start] is None or cost<dp[start][0]:
                dp[start]=(cost,[stop]+dp[stop][1])
    if dp[0] is None:
        return None
    result=[]
    start=0
    for stop in dp[0][1]:
        result.append(" ".join(phrases[start:stop]))
        start=stop
    return result


def split_scene(narration):
    pieces=SENTENCE_BREAK.split(narration)
    candidates=partition(pieces)
    if candidates is None:
        # Introducir cortes de respiración solo en comas ya escritas.
        clauses=[token for sentence in pieces for token in CLAUSE_BREAK.split(sentence)]
        candidates=partition(clauses)
    if candidates is None:
        # No forzar un lote inaudible: reportar fallo y exigir intervención.
        raise ValueError("La escena requiere revisión manual de segmentación, no cortar palabras")
    if not 2<=len(candidates)<=MAX_CLIPS_PER_SCENE:
        raise ValueError("La escena excede presupuesto de 2-8 clips")
    if " ".join(candidates)!=narration:
        raise RuntimeError("Se perdió contenido del manuscrito")
    if sum(map(len,candidates))>MAX_BATCH_CHARS:
        raise ValueError("Excede límite de caracteres por escena")
    return candidates


def make_schedule(source_text):
    scenes=all_scene_voices(source_text)
    batches=[]
    for n,title,voice in scenes:
        chunks=split_scene(voice)
        batches.append({
            "scene":n,"title":title,
            "source_manuscript_sha256":hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "narration_words":len(voice.split()),
            "parts":[{"id":f"S{n:02d}_P{i:02d}","text":piece,
                      "characters":len(piece),"voice_state":"not_generated"}
                     for i,piece in enumerate(chunks,1)],
            "render_status":"blocked_pending_voice_review",
            "voice_reference_required":"canonical_sha256",
            "rights_verified":False,
        })
    return {
        "project":"Factor de Gigantes","episode":"BlackBerry",
        "scenes":batches,"scenes_count":len(batches),
        "total_words":sum(b["narration_words"] for b in batches),
        "planned_voice_clips":sum(len(b["parts"]) for b in batches),
        "max_scene_clips":max(len(b["parts"]) for b in batches),
        "cpu_strategy":"one_scene_per_manual_job_no_parallel_model_downloads",
        "generated_voice_clips":0,
        "human_voice_approval":False,
        "commercial_rights_verified":False,
        "documentary_complete":False,
        "youtube_publication_allowed":False,
        "warning":"Solo agenda técnica: audición humana, licencias y hechos todavía pendientes."
    }


def main():
    parser=argparse.ArgumentParser(description="Planificar 12 lotes BlackBerry sin ejecutar TTS")
    parser.add_argument("--script",type=Path,default=DEFAULT_SCRIPT)
    parser.add_argument("--out",type=Path,
        default=Path("dist/blackberry-narration/SCHEDULE_12_SCENES.json"))
    args=parser.parse_args()
    schedule=make_schedule(args.script.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(schedule,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PLAN_VOZ:",schedule["scenes_count"],"escenas;",
          schedule["planned_voice_clips"],"fragmentos;",
          "sintetizados:",schedule["generated_voice_clips"],
          "YOUTUBE:",schedule["youtube_publication_allowed"])


if __name__=="__main__":
    main()
