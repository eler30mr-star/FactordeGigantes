"""Comprobador editorial determinista del guion BlackBerry.

Verifica estructura, citas, tiempos y puertas de aprobación. No verifica
verdad histórica, licencias ni calidad de la locución; no genera audio/video.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

HEADER=re.compile(r"^## Escena (\d{2}) · ([^\n]+?) \((\d{2}:\d{2})–(\d{2}:\d{2})\)$",re.M)
TOKEN=re.compile(r"^\[[A-Z0-9]{2,8}\]$")
DEFAULT_SCRIPT=Path("research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md")
DEFAULT_SOURCES=Path("research/blackberry/FUENTES_GUION_10MIN.json")


def clock(s):
    mins,sec=s.split(":")
    if int(sec)>=60:
        raise ValueError("Segundo de reloj incorrecto")
    return int(mins)*60+int(sec)


def inspect_script(text,registry):
    if not isinstance(text,str) or not isinstance(registry,dict):
        raise ValueError("Documento inválido")
    sources=registry.get("citations",[])
    if not isinstance(sources,list):
        raise ValueError("Fuentes no válidas")
    lookup={}
    for item in sources:
        if not isinstance(item,dict):
            raise ValueError("Entrada de fuente no válida")
        sid=item.get("id")
        if not isinstance(sid,str) or not re.fullmatch(r"[A-Z0-9]{2,8}",sid) or sid in lookup:
            raise ValueError("ID de fuente incorrecto o duplicado")
        if not isinstance(item.get("url"),str) or not item["url"].startswith("https://"):
            raise ValueError("Solo fuentes https en el registro")
        lookup[sid]=item
    matches=list(HEADER.finditer(text))
    scene_reports=[]
    flags=[]
    for i,match in enumerate(matches,1):
        begin=match.end()
        end=matches[i].start() if i<len(matches) else text.find("\n---",begin)
        if end==-1:end=len(text)
        body=text[begin:end]
        voice_match=re.search(r"\*\*NARRADOR\*\*\s+(.+?)\s+\*\*FUENTES POR COMPROBAR:\*\*\s+([^\n]+)",body,re.S)
        if voice_match is None:
            flags.append(f"escena_{i}_sin_voz_o_fuentes")
            continue
        voice=voice_match.group(1).strip()
        refs=[x.strip() for x in voice_match.group(2).split()]
        used={x[1:-1] for x in refs if TOKEN.fullmatch(x)}
        if any(x not in lookup for x in used) or len(used)!=len(refs) or not used:
            flags.append(f"escena_{i}_sin_citas_validas")
        if match.group(1)!=str(i).zfill(2):
            flags.append(f"escena_{i}_numero_incorrecto")
        start,end_clock=clock(match.group(3)),clock(match.group(4))
        seconds=end_clock-start
        if seconds<=0:
            flags.append(f"escena_{i}_reloj_invertido")
        word_count=len(voice.split())
        pace=round(word_count*60/seconds,1) if seconds>0 else None
        if pace is None or not (110<=pace<=175):
            flags.append(f"escena_{i}_ritmo_a_revisar")
        scene_reports.append({
            "scene":i,"title":match.group(2),"begin_s":start,"end_s":end_clock,
            "seconds":seconds,"words":word_count,"words_per_minute_target":pace,
            "source_ids":sorted(used)
        })
    if len(scene_reports)!=12:
        flags.append("requiere_12_escenas_completas")
    for first,second in zip(scene_reports,scene_reports[1:]):
        if first["end_s"]!=second["begin_s"]:
            flags.append(f"corte_no_contiguo_{first['scene']}_{second['scene']}")
    duration=scene_reports[-1]["end_s"] if scene_reports else 0
    total_words=sum(scene["words"] for scene in scene_reports)
    if not (600<=duration<=840):
        flags.append("duracion_fuera_de_8_a_14")
    if not (1500<=total_words<=1900):
        flags.append("texto_no_corresponde_a_documental_largo")
    required={"F24","F25","K25","H99","D16"}
    referenced={ref for sc in scene_reports for ref in sc["source_ids"]}
    if not required.issubset(referenced):
        flags.append("faltan_fuentes_nucleares")
    if "853" not in text or "759" not in text or "no" not in text.lower():
        # Los números están en palabras en la narración; criterio de seguridad
        # específico exige una alerta explícita por presentación comparativa.
        if "comparativ" not in text.lower() or "perímetro" not in text.lower():
            flags.append("falta_advertencia_comparabilidad")
    if not all(token in text for token in ("NO APROBADO","No usar imágenes","revisión factual humana")):
        flags.append("faltan_bloqueos_editoriales")
    return {
        "product":"Factor de Gigantes","document":"BlackBerry documentary, internal only",
        "scenes":scene_reports, "scene_count":len(scene_reports),
        "total_words":total_words,"timeline_seconds":duration,
        "target_avg_wpm":round(total_words*60/duration,1) if duration else None,
        "distinct_sources_used":len(referenced),
        "flags":sorted(set(flags)), "structural_gate_passed":not flags,
        "factual_gate_passed":False, "commercial_voice_license_verified":False,
        "visual_rights_verified":False, "render_authorized":False,
        "youtube_publication_authorized":False,
        "notice":"Prueba estructural: nunca confundir con verificación factual o de derechos."
    }


def main():
    parser=argparse.ArgumentParser(description="QA estático del primer guion largo BlackBerry")
    parser.add_argument("--script",type=Path,default=DEFAULT_SCRIPT)
    parser.add_argument("--sources",type=Path,default=DEFAULT_SOURCES)
    parser.add_argument("--out",type=Path,default=Path("dist/blackberry-script"))
    args=parser.parse_args()
    report=inspect_script(args.script.read_text(encoding="utf-8"),
                          json.loads(args.sources.read_text(encoding="utf-8")))
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"QA_ESTRUCTURAL_GUION.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GUION:",report["scene_count"],"escenas;",
          report["total_words"],"palabras;",report["timeline_seconds"],"segundos")
    print("CITAS_DISTINTAS:",report["distinct_sources_used"],"ALERTAS:",report["flags"])
    print("APROBADO PARA PUBLICAR:",report["youtube_publication_authorized"])
    if not report["structural_gate_passed"]:
        raise SystemExit("El guion contiene anomalías estructurales")


if __name__=="__main__":
    main()
