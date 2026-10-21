"""Inspección de un documento PDF externo: informe mínimo con localizadores reales.

Permite ensayar documentos primarios sin convertir su contenido en una
afirmación automáticamente verdadera.
"""
import argparse
import hashlib
import json
from pathlib import Path

from tools.pdf_sources import (
    analyze_document, fetch_document_public, page_cited_matches,
)
from tools.research_engine import excerpts_for_claim


def inspect_pdf(url, query, fetcher=fetch_document_public):
    raw, resolved, mime = fetcher(url)
    if mime != "application/pdf":
        raise ValueError("El documento solicitado no devolvió application/pdf")
    analyzed=analyze_document(raw,mime)
    if analyzed["type"]!="pdf":
        raise ValueError("Solo se inspeccionan PDFs")
    passages=page_cited_matches(query,analyzed,matcher=excerpts_for_claim)
    return {
        "product":"Factor de Gigantes", "document_url":resolved,
        "document_sha256":hashlib.sha256(raw).hexdigest(),
        "pdf_bytes":len(raw), "pages":analyzed["total_pages"],
        "readable_blocks":len(analyzed["blocks"]),
        "question":query, "candidate_passages":passages,
        "facts_verified":0, "rights_verified":0,
        "owner_approval":False, "publication_authorized":False,
        "notes":"Solo búsqueda textual y localización por página; no verifica hechos, causalidad ni derechos."
    }


def main():
    parser=argparse.ArgumentParser(description="Inspeccionar PDF original con citas por página")
    parser.add_argument("--url",required=True)
    parser.add_argument("--query",required=True)
    parser.add_argument("--out",type=Path,default=Path("dist/documento-pdf"))
    opts=parser.parse_args()
    if not 15<=len(opts.query)<=250:
        parser.error("La pregunta debe medir entre 15 y 250 caracteres")
    report=inspect_pdf(opts.url,opts.query)
    opts.out.mkdir(parents=True,exist_ok=True)
    (opts.out/"reporte_pdf_citado.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PDF_EVIDENCIA:",report["pages"],"páginas,",
          report["readable_blocks"],"bloques,",
          len(report["candidate_passages"]),"pasajes posibles.",flush=True)
    for passage in report["candidate_passages"]:
        print("PASAJE:",passage["locator"],"similitud:",passage["similarity"],
              passage["excerpt"][:95],flush=True)
    print("VERIFICADOS: 0, PUBLICACION: NO",flush=True)


if __name__=="__main__":
    main()
