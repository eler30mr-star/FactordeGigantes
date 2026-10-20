"""Identidad del narrador aprobado; nunca sustituir silenciosamente por otra voz."""
import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets"/"voice"/"approved"
FILE_NAME="narrador_documental_aprobado.mp3"
SHA="78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d"
BYTES=247245
TRANSCRIPT="Durante años, Blákberri parecía invencible. Sus decisiones definían el futuro de la comunicación. Hasta que una nueva generación cambió las reglas. Esto es Factor de Gigantes."

def hash_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def approved_reference(folder=FOLDER):
    folder=Path(folder)
    metadata=json.loads((folder/"reference.json").read_text(encoding="utf-8"))
    if metadata.get("status")!="approved_by_owner_for_editorial_reference":
        raise RuntimeError("El propietario aún no aprobó esta referencia")
    if metadata.get("file")!=FILE_NAME or metadata.get("sha256")!=SHA or metadata.get("reference_text")!=TRANSCRIPT:
        raise RuntimeError("Identidad de referencia inconsistente")
    audio=folder/FILE_NAME
    if not audio.is_file() or audio.stat().st_size!=BYTES or hash_file(audio)!=SHA:
        raise RuntimeError("Falta la voz aprobada o su contenido ha cambiado")
    return audio, metadata

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true",required=True)
    parser.parse_args()
    audio,metadata=approved_reference()
    print(json.dumps({"file":str(audio),"sha256":hash_file(audio),"status":metadata["status"]},ensure_ascii=False))
