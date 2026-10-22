"""Evidencia documental acotada desde links P856 ya detectados por Factor.

Solo informes PDF enlazados en HTML corporativo, mismo hostname. Conserva
SHA-256, página real, bloque y fragmento; son afirmaciones *por corroborar*.
No genera guion, no verifica hechos ni licencia y no reutiliza PDFs audiovisualmente.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib.parse import urlsplit
from tools.pdf_sources import analyze_document,fetch_document_public
from tools.research_engine import validate_url

MAX_DOCS=2
MAX_FRAGMENTS_PER_DOC=5
MAX_SNIPPET=320
MAX_PAGES=350
ID=re.compile(r"^Q[1-9][0-9]*$")

def select_pdf_candidates(official,primary_pages=None):
    if not isinstance(official,dict) or official.get("provider")!="wikidata_p856_safe_official_fetch_v1":
        raise ValueError("Se requiere evidencia oficial del radar")
    if official.get("primary_facts_verified")!=0 or official.get("ready_for_youtube") is not False:
        raise ValueError("El radar no ha verificado fuentes")
    rows=list(official.get("evidence",[])[:3])
    if primary_pages is not None:
        if (primary_pages.get("provider")!="official_investor_pages_v1" or
            primary_pages.get("collected_on")!=official.get("collected_on") or
            primary_pages.get("facts_verified")!=0 or
            primary_pages.get("rights_verified") is not False or
            primary_pages.get("ready_for_youtube") is not False):
            raise ValueError("Páginas de informes sin procedencia compatible")
        allowed={r.get("wikidata_id"):r for r in rows if isinstance(r,dict)}
        for page in primary_pages.get("pages",[])[:3]:
            source=allowed.get(page.get("wikidata_id"))
            if not source or page.get("status") not in {"excerpt_candidate","low_information"}:continue
            origin=source.get("resolved_url")
            resolved=page.get("resolved_url")
            if page.get("origin_url")!=origin:continue
            try:
                validate_url(resolved)
                if urlsplit(resolved).hostname!=urlsplit(origin).hostname:continue
            except (ValueError,TypeError):continue
            rows.append({**page,"company":source["company"],"status":"candidate_page_readable"})
    selected=[];seen=set()
    for item in rows:
        if not isinstance(item,dict) or not ID.fullmatch(str(item.get("wikidata_id",""))) or \
           item.get("status")!="candidate_page_readable":continue
        origin=item.get("resolved_url")
        if not isinstance(origin,str):continue
        validate_url(origin)
        host=urlsplit(origin).hostname
        for candidate in item.get("document_link_candidates",[])[:4]:
            if not isinstance(candidate,dict) or candidate.get("document_fetched") is not False or \
               candidate.get("ownership_verified") is not False:continue
            url=candidate.get("url")
            try:
                validate_url(url)
                parsed=urlsplit(url)
                if parsed.hostname!=host or not parsed.path.lower().endswith(".pdf"):
                    continue
            except (ValueError,TypeError,OverflowError):continue
            if url in seen:continue
            seen.add(url)
            selected.append({"wikidata_id":item["wikidata_id"],"company":item["company"],
              "source_page":origin,"document_url":url})
            break
        if len(selected)>=MAX_DOCS:break
    return selected

def extract_document_evidence(official, *,primary_pages=None,fetcher=fetch_document_public):
    candidates=select_pdf_candidates(official,primary_pages)
    documents=[]
    for item in candidates:
        record={**item,"state":"fetch_failed","resolved_url":None,
          "sha256":None,"pages_total":None,"fragments":[],
          "facts_verified":0,"copyright_permission_verified":False}
        try:
            payload,resolved,mime=fetcher(item["document_url"],timeout=14)
            validate_url(resolved)
            if mime!="application/pdf" or urlsplit(resolved).hostname!=urlsplit(item["source_page"]).hostname:
                raise ValueError("Informe PDF fuera de dominio permitido")
            info=analyze_document(payload,mime)
            if info["type"]!="pdf" or info["total_pages"] is None or \
                    info["total_pages"]>MAX_PAGES:raise ValueError("PDF fuera de límites")
            options=[]
            for i,(block,page) in enumerate(zip(info["blocks"],info["page_map"])):
                text=" ".join(str(block).split())
                # Evita encabezados sin contexto y textos minúsculos.
                if page is None or len(text)<90 or len(text)>5000:continue
                options.append({"page":page,"block_index":i,
                  "locator":"PDF página "+str(page)+", bloque "+str(i+1),
                  "excerpt":text[:MAX_SNIPPET],"verification_state":"uncorroborated"})
                if len(options)>=MAX_FRAGMENTS_PER_DOC:break
            record.update({"state":"text_extracted" if options else "pdf_without_usable_text",
              "resolved_url":resolved,"sha256":hashlib.sha256(payload).hexdigest(),
              "pages_total":info["total_pages"],"fragments":options})
        except (OSError,TimeoutError,ValueError,TypeError,UnicodeError,KeyError,ImportError,RuntimeError) as exc:
            record["error_type"]=type(exc).__name__
        documents.append(record)
    return {"provider":"official_pdf_evidence_v1",
       "collected_on":official["collected_on"],"attempted":len(documents),
       "text_extracted":sum(d["state"]=="text_extracted" for d in documents),
       "documents":documents,"verified_claim_count":0,
       "research_ready":False,"script_authorized":False,
       "publication_authorized":False,
       "warning":"Fragmentos textuales observados en PDF público; requieren corroboración del origen, fecha, significado y derechos."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--official",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--primary-pages",type=Path)
    a=parser.parse_args()
    primary=json.loads(a.primary_pages.read_text(encoding="utf-8")) if a.primary_pages else None
    result=extract_document_evidence(json.loads(a.official.read_text(encoding="utf-8")),primary_pages=primary)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PDF_CANDIDATOS:",result["attempted"],"PDF_CON_FRAGMENTOS:",
          result["text_extracted"],"HECHOS_VERIFICADOS:",result["verified_claim_count"])

if __name__=="__main__":main()

