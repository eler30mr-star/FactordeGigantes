"""Puente autónomo: PDFs corporativos del radar -> investigador Gemini gratuito.

Los pasajes llevan E###, URL original, página, hash y nombre empresarial.
Si no hay páginas textuales no se envía nada a un LLM. Sin autorización
explícita de modalidad sin facturación, no se llama a API alguna.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re
from pathlib import Path
from tools.research_providers import run_gemini_free

MAX_EVIDENCE=10
QID=re.compile(r"^Q[1-9][0-9]*$")
SHA=re.compile(r"^[0-9a-f]{64}$")

def prepare_evidence(pdf_report):
    if not isinstance(pdf_report,dict) or pdf_report.get("provider")!="official_pdf_evidence_v1" or \
      pdf_report.get("verified_claim_count")!=0 or pdf_report.get("publication_authorized") is not False:
        raise ValueError("Únicamente PDFs de radar sin autorización editorial")
    items=[]
    for doc in pdf_report.get("documents",[])[:2]:
        if doc.get("state")!="text_extracted":continue
        if not QID.fullmatch(str(doc.get("wikidata_id",""))) or \
           not SHA.fullmatch(str(doc.get("sha256",""))):
            continue
        url=doc.get("resolved_url")
        if not isinstance(url,str) or not url.startswith("https://"):continue
        for fragment in doc.get("fragments",[])[:5]:
            snippet=fragment.get("excerpt")
            page=fragment.get("page")
            if fragment.get("verification_state")!="uncorroborated" or \
               not isinstance(page,int) or page<1 or \
               not isinstance(snippet,str) or len(snippet.strip())<90:continue
            items.append({"id":f"E{len(items)+1:03d}",
              "source_id":doc["wikidata_id"]+"-pdf",
              "claim_id":"documentary_candidate",
              "url":url,"page":page,
              "excerpt":snippet[:320],
              "document_sha256":doc["sha256"],
              "wikidata_id":doc["wikidata_id"],"company":doc["company"]})
            if len(items)>=MAX_EVIDENCE:break
        if len(items)>=MAX_EVIDENCE:break
    return items

def run_investigation(pdf_report,*,free_confirmed=False,api_key=None,model="gemini-2.5-flash-lite",
                      runner=run_gemini_free):
    evidence=prepare_evidence(pdf_report)
    if not evidence:
        return {"status":"skipped_no_documentary_evidence","provider":None,
          "evidence_count":0,"candidate_claims":[],
          "facts_verified_automatically":0,"ready_for_script":False,
          "publication_authorized":False}
    if not free_confirmed or not isinstance(api_key,str) or len(api_key)<15:
        return {"status":"skipped_free_tier_not_authorized","provider":None,
          "evidence_count":len(evidence),"candidate_claims":[],
          "facts_verified_automatically":0,"ready_for_script":False,
          "publication_authorized":False}
    # Tema deducido de entidades encontradas, no proporcionado por ChatGPT.
    topic=", ".join(dict.fromkeys(item["company"] for item in evidence))[:130]
    result=runner(topic,evidence,api_key=api_key,model=model,free_tier_confirmed=True)
    if (result.get("facts_verified_automatically")!=0 or
        result.get("ready_for_script") is not False or
        result.get("ready_for_youtube") is not False):
        raise ValueError("Investigador intentó declarar hechos o contenido listo")
    return {**result,"status":"candidate_claims_generated",
      "origin":"official_pdf_evidence_v1",
      "input_evidence":[{k:v for k,v in e.items() if k not in ("excerpt",)} for e in evidence],
      "publication_authorized":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf-report",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    input_data=json.loads(a.pdf_report.read_text(encoding="utf-8"))
    authorized=os.getenv("GEMINI_RESEARCH_FREE_CONFIRMED")=="1"
    key=os.getenv("GEMINI_API_KEY")
    try:
        out=run_investigation(input_data,free_confirmed=authorized,api_key=key)
    except (OSError,ValueError,RuntimeError,KeyError,TypeError) as exc:
        # Nunca registrar cuerpo remoto, token de cabecera o prompt sin consentimiento.
        out={"status":"research_provider_failure","error_type":type(exc).__name__,
             "candidate_claims":[],"facts_verified_automatically":0,
             "ready_for_script":False,"publication_authorized":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("INVESTIGADOR:",out["status"],
          "HECHOS_VERIFICADOS:",out["facts_verified_automatically"],
          "LISTO_PARA_GUION:",out["ready_for_script"])

if __name__=="__main__":main()
