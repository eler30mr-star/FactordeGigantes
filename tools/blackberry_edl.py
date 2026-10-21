"""Plan de edición temporal derivado del guion revisable BlackBerry.

No crea video, no recorta fuentes, no usa imágenes ajenas ni abre YouTube.
Alimenta un eventual renderizador con escenas y tareas visuales bien delimitadas.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from tools.blackberry_script_quality import (
    DEFAULT_SCRIPT, DEFAULT_SOURCES, HEADER, inspect_script
)

VISUAL=re.compile(r"\*\*VISUAL PROPUESTO, SIN LICENCIA PRESUPUESTA:\*\*\s+([^\n]+)")


def make_edl(script, sources):
    qa=inspect_script(script,sources)
    if not qa["structural_gate_passed"]:
        raise ValueError("No crear EDL desde guion con anomalías estructurales")
    markers=list(HEADER.finditer(script))
    shots=[]
    for idx,mark in enumerate(markers):
        end=markers[idx+1].start() if idx+1<len(markers) else script.find("\n---",mark.end())
        if end<0:end=len(script)
        body=script[mark.end():end]
        visual=VISUAL.search(body)
        if visual is None:
            raise ValueError(f"La escena {idx+1} no tiene visual documentado")
        record=qa["scenes"][idx]
        shots.append({
            "scene_id":f"SC{idx+1:02d}",
            "title":record["title"],
            "start_ms":record["begin_s"]*1000,
            "end_ms":record["end_s"]*1000,
            "duration_ms":record["seconds"]*1000,
            "narration_word_count":record["words"],
            "voice_reference_source":"documentary_narrator_pending_commercial_license",
            "suggested_visual":visual.group(1).strip(),
            "visual_status":"requires_original_creation_or_verified_license",
            "source_ids":record["source_ids"],
            "footage_attached":False,
            "voice_track_attached":False,
            "music_attached":False,
            "render_allowed":False,
        })
    return {
        "product":"Factor de Gigantes",
        "episode":"BlackBerry — La empresa que sobrevivió a su teléfono",
        "version":1,
        "timeline_duration_ms":qa["timeline_seconds"]*1000,
        "scenes":shots,
        "original_narration_words":qa["total_words"],
        "structural_checks_passed":True,
        "human_factual_approval":False,
        "voice_commercial_rights_verified":False,
        "music_rights_verified":False,
        "visual_rights_verified":False,
        "ready_for_commercial_export":False,
        "upload_to_youtube":False,
        "warning":"Cronograma para producción futura. No contiene audio/video ni licencias."
    }


def main():
    p=argparse.ArgumentParser(description="Exportar EDL revisable y segura desde guion BlackBerry")
    p.add_argument("--script",type=Path,default=DEFAULT_SCRIPT)
    p.add_argument("--sources",type=Path,default=DEFAULT_SOURCES)
    p.add_argument("--out",type=Path,default=Path("dist/blackberry-script"))
    args=p.parse_args()
    edl=make_edl(args.script.read_text(encoding="utf-8"),
                 json.loads(args.sources.read_text(encoding="utf-8")))
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"EDL_PREVIA_12_ESCENAS.json").write_text(
        json.dumps(edl,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EDL:",len(edl["scenes"]),"escenas",
          edl["timeline_duration_ms"],"ms; fuentes y derechos pendientes")


if __name__=="__main__":
    main()
