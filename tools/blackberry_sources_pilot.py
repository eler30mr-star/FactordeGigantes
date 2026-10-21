"""Piloto BlackBerry: dos comunicados financieros PDF del portal de inversores.

Una extracción corroborada con números/página nunca equivale a aprobación
editorial, licencia comercial, narración ni material para YouTube.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError

from tools.pdf_sources import fetch_document_public, pdf_page_blocks

SOURCES = (
    {"id": "BB_FY24", "reporting_date": "2024-04-03", "document": "BlackBerry Q4/FY2024 Earnings Release",
     "url": "https://irp.cdn-website.com/586e2b1b/files/uploaded/Q4-FY24-Earnings-Press-Release.pdf",
     "period_end": "2024-02-29", "publisher": "BlackBerry Investor Relations"},
    {"id": "BB_FY25", "reporting_date": "2025-04-02", "document": "BlackBerry Q4/FY2025 Earnings Release",
     "url": "https://irp.cdn-website.com/586e2b1b/files/uploaded/Q4_FY25_Earnings_Press_Release_-_FINAL-7064fd77.pdf",
     "period_end": "2025-02-28", "publisher": "BlackBerry Investor Relations"}
)
# Página física de PDF (base 1), no numeración de secciones o impresa.
# No comparar automáticamente FY24 original y FY24 recast: cambió el perímetro.
FACTS = (
    {"id":"BB24_REV_ORIGINAL","source_id":"BB_FY24","page":2,
     "amount_millions":"853","metric":"total_company_revenue",
     "scope":"as_reported_apr_2024_including_legacy_patent_sale",
     "period_end":"2024-02-29",
     "pattern":r"Total company revenue was\s*\$?\s*853(?:\.0)?\s+million"},
    {"id":"BB24_PATENT_REVENUE","source_id":"BB_FY24","page":2,
     "amount_millions":"218","metric":"legacy_patent_portfolio_sale_included_in_revenue",
     "scope":"as_reported_apr_2024","period_end":"2024-02-29",
     "pattern":r"including\s*\$?\s*218(?:\.0)?\s+million"},
    {"id":"BB25_REV","source_id":"BB_FY25","page":2,
     "amount_millions":"534.9","metric":"total_company_revenue",
     "scope":"fy2025_company_results_represented_apr_2025",
     "period_end":"2025-02-28",
     "pattern":r"Total company revenue for the full fiscal year was\s*\$?\s*534\.9\s+million"},
    {"id":"BB25_QNX_REV","source_id":"BB_FY25","page":2,
     "amount_millions":"236.0","metric":"QNX_division_revenue",
     "scope":"fy2025_division_results_apr_2025",
     "period_end":"2025-02-28",
     "pattern":r"QNX revenue for the full fiscal year.{0,180}?\$?\s*236\.0\s+million"},
    {"id":"BB24_REV_RECAST","source_id":"BB_FY25","page":16,
     "amount_millions":"759.1","metric":"total_company_revenue",
     "scope":"fy2024_comparative_recast_in_apr_2025_report",
     "period_end":"2024-02-29",
     "pattern":r"Revenue\s+\$?\s*534\.9\s+\$?\s*759\.1"},
)

def scan(source_files, *, reader=pdf_page_blocks):
    """source_files: id -> (raw, final_url, MIME). Missing source yields NO facts."""
    sources=[]
    facts=[]
    for source in SOURCES:
        record={k:v for k,v in source.items()}
        record.update({"download_status":"unavailable","text_readable":False,
                       "copyright_cleared":False})
        try:
            raw,resolved,mime=source_files[source["id"]]
            if resolved!=source["url"] or mime.split(";")[0].lower().strip()!="application/pdf":
                raise ValueError("PDF oficial cambió URL o MIME")
            if not isinstance(raw,bytes):
                raise ValueError("Payload PDF inválido")
            blocks,pages,page_count=reader(raw)
            record.update({"download_status":"fetched","text_readable":len(blocks)>0,
                           "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
                           "pdf_pages":page_count,"text_blocks":len(blocks)})
            indexed={}
            for block,page in zip(blocks,pages):
                indexed.setdefault(page,[]).append(block)
            for criterion in FACTS:
                if criterion["source_id"]!=source["id"]:
                    continue
                page=criterion["page"]
                if page>page_count:
                    continue
                content=" ".join(indexed.get(page,[]))
                normalized=re.sub(r"\s+"," ",content)
                if re.search(criterion["pattern"],normalized,re.I):
                    facts.append({
                        "id":criterion["id"],"source_id":source["id"],
                        "source_url":source["url"],"sha256":record["sha256"],
                        "pdf_page":page,
                        "value_millions_usd":criterion["amount_millions"],
                        "metric":criterion["metric"],"period_end":criterion["period_end"],
                        "accounting_scope":criterion["scope"],
                        "machine_matched_original_pdf":True,"human_verified":False,
                        "license_for_audiovisual_reuse_verified":False
                    })
        except (KeyError,ValueError,OSError,UnicodeError,TimeoutError) as exc:
            record["download_status"]="unavailable"
            record["error_type"]=type(exc).__name__
        sources.append(record)
    matched={x["id"] for x in facts}
    missing=[x["id"] for x in FACTS if x["id"] not in matched]
    return {
        "product":"Factor de Gigantes","topic":"La transformación de BlackBerry",
        "documents":sources,
        "facts_located":len(facts),"facts":facts,
        "missing_evidence_ids":missing,
        "comparability_warning":(
            "FY24 revenue as announced in April 2024 (853m) and FY24 comparative "
            "restated in the FY25 document (759.1m) have different reporting scopes. "
            "Do not calculate growth/decline from these two presentations; review "
            "discontinued operations and financial notes before comparisons."
        ),
        "verified_by_human":0,"automatic_facts_approved":0,
        "filming_rights_verified":False,"narration_rights_verified":False,
        "ready_for_render":False,"ready_for_youtube":False
    }


def run(*,fetcher=fetch_document_public):
    items={}
    for source in SOURCES:
        try:
            items[source["id"]]=fetcher(source["url"])
        except (HTTPError,URLError,OSError,ValueError,TimeoutError,UnicodeError):
            pass
    return scan(items)


def main():
    p=argparse.ArgumentParser(description="Extraer hechos candidatos de comunicados originales de BlackBerry")
    p.add_argument("--out",type=Path,default=Path("dist/blackberry-real"))
    opts=p.parse_args()
    opts.out.mkdir(parents=True,exist_ok=True)
    result=run()
    (opts.out/"HECHOS_BLACKBERRY_2024_2025_CON_PAGINAS.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FUENTES_PDF_ORIGINALES:",sum(s["download_status"]=="fetched" for s in result["documents"]))
    print("DATOS_CON_PAGINA:",result["facts_located"],"de",len(FACTS))
    print("DATOS_FALTANTES:",",".join(result["missing_evidence_ids"]) or "ninguno")
    print("VERIFICACION_HUMANA: 0; VIDEO_PUBLICABLE: NO")

if __name__=="__main__":
    main()
