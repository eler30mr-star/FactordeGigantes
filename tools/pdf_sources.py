"""Fuentes PDF públicas con localizadores de página para Factor de Gigantes.

Solo extracción TEXTUAL de PDFs pequeños. No OCR, no imágenes, no páginas
completas en artefactos, no uso comercial inferido ni verificación automática.
"""
from __future__ import annotations

import hashlib
from io import BytesIO
import re
import ssl
from urllib.parse import urlsplit
from urllib.request import Request, HTTPSHandler, build_opener

from tools.research_engine import (
    USER_AGENT, MAX_BYTES, MAX_EXCERPT_CHARS,
    PublicRedirects, check_public_dns, validate_url,
)

MAX_PDF_BYTES = 4_000_000
MAX_PDF_PAGES = 35
MAX_PAGE_TEXT = 9000
MAX_PDF_TEXT = 100_000
MAX_PDF_BLOCKS = 500
MAX_BLOCK_TEXT = 1250

VALID_TEXT_TYPES = ("text/html", "text/plain", "application/json")


def fetch_document_public(url: str, *, timeout: int = 14):
    """Downloader acotado, con la misma validación DNS/redirect que el motor HTML.

    Fija Content-Encoding identity; PDF tiene un presupuesto mayor que HTML,
    pero no descarga sin límite ni acepta otros binarios.
    """
    validate_url(url)
    check_public_dns(urlsplit(url).hostname)
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), PublicRedirects())
    req = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,text/html;q=0.9,text/plain;q=0.8,application/json;q=0.7",
        "Accept-Encoding": "identity",
    })
    with opener.open(req, timeout=timeout) as response:
        final_url = validate_url(response.geturl())
        mime = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        is_pdf = mime == "application/pdf"
        if mime not in VALID_TEXT_TYPES and not is_pdf:
            raise ValueError("MIME no permitido para investigación documental")
        budget = MAX_PDF_BYTES if is_pdf else MAX_BYTES
        declared = response.headers.get("Content-Length")
        if declared is not None and (not declared.isdigit() or int(declared) > budget):
            raise ValueError("Tamaño declarado supera presupuesto")
        raw = response.read(budget + 1)
        if len(raw) > budget:
            raise ValueError("Documento remoto demasiado grande")
        if is_pdf and not raw.startswith(b"%PDF-"):
            raise ValueError("El documento anuncia PDF pero su cabecera no es PDF")
        if not is_pdf and raw.startswith(b"%PDF-"):
            raise ValueError("PDF servido con tipo de contenido incorrecto")
        return raw, final_url, mime


def pdf_page_blocks(raw: bytes, *, max_pages=None, scan_pages=None) -> tuple[list[str], list[int], int]:
    """Lista de bloques textuales, página real (base 1) y total de páginas."""
    if not isinstance(raw, bytes) or not raw.startswith(b"%PDF-"):
        raise ValueError("No es un documento PDF válido")
    if len(raw) > MAX_PDF_BYTES:
        raise ValueError("PDF excede el límite de tamaño")
    if max_pages is None:max_pages=MAX_PDF_PAGES
    if (type(max_pages) is not int or not 1<=max_pages<=350 or
        scan_pages is not None and (type(scan_pages) is not int or not 1<=scan_pages<=35)):
        raise ValueError("Presupuesto de páginas inválido")
    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(raw), strict=True)
        if reader.is_encrypted:
            raise ValueError("PDF cifrado: no procesar")
        page_count = len(reader.pages)
        if not 1 <= page_count <= max_pages:
            raise ValueError("Cantidad de páginas PDF fuera del presupuesto")
        blocks, pages = [], []
        text_total = 0
        for page_number, page in enumerate(reader.pages, 1):
            if scan_pages is not None and page_number>scan_pages:break
            page_text = page.extract_text() or ""
            # Rechazar un documento que sobrepasa límites antes de almacenar texto.
            if len(page_text) > MAX_PAGE_TEXT:
                page_text = page_text[:MAX_PAGE_TEXT]
            text_total += len(page_text)
            if text_total > MAX_PDF_TEXT:
                raise ValueError("Extracción PDF excede presupuesto textual")
            page_text = page_text.replace("\x00", " ")
            for part in re.split(r"(?<=\.)\s+|\n{2,}", page_text):
                block = re.sub(r"\s+", " ", part).strip()
                if len(block) < 35:
                    continue
                if len(block) > MAX_BLOCK_TEXT:
                    block = block[:MAX_BLOCK_TEXT]
                blocks.append(block)
                pages.append(page_number)
                if len(blocks) >= MAX_PDF_BLOCKS:
                    return blocks, pages, page_count
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("El PDF no pudo analizarse con seguridad") from exc
    return blocks, pages, page_count


def pdf_link_annotations(raw: bytes, *, max_pages=350, scan_pages=12):
    """URLs literales de anotaciones Link/URI, sin ejecutar acciones del PDF."""
    if not isinstance(raw, bytes) or not raw.startswith(b'%PDF-') or len(raw)>MAX_PDF_BYTES:
        raise ValueError('PDF fuera del presupuesto de referencias')
    if (type(scan_pages) is not int or not 1<=scan_pages<=35 or
            type(max_pages) is not int or not 1<=max_pages<=350):
        raise ValueError('Presupuesto de referencias PDF inválido')
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError
    try:
        reader=PdfReader(BytesIO(raw),strict=True)
        if reader.is_encrypted or not 1<=len(reader.pages)<=max_pages:
            raise ValueError('PDF cifrado o demasiado extenso')
    except PyPdfError:
        raise ValueError('No se pudieron leer las referencias PDF') from None
    links=[]
    for n,page in enumerate(reader.pages,1):
        if n>scan_pages:break
        annotations=page.get('/Annots',[])
        if not isinstance(annotations,list):continue
        for ref in annotations[:64]:
            try:
                item=ref.get_object()
                action=item.get('/A')
                if hasattr(action,'get_object'):action=action.get_object()
                if item.get('/Subtype')!='/Link' or not isinstance(action,dict) or action.get('/S')!='/URI':
                    continue
                url=action.get('/URI')
                if isinstance(url,str) and len(url)<=1000:
                    links.append({'url':url,'page':n})
                if len(links)>=64:return links
            except (ValueError,TypeError,KeyError,AttributeError,RecursionError,PyPdfError):
                continue
    return links


def analyze_document(raw: bytes, mime: str, *, pdf_max_pages=None, pdf_scan_pages=None):
    """Contrato uniforme para HTML y PDF: bloques, páginas por bloque, total."""
    if mime.split(";", 1)[0].strip().lower() == "application/pdf":
        blocks, page_map, total = pdf_page_blocks(raw,max_pages=pdf_max_pages,scan_pages=pdf_scan_pages)
        return {"blocks": blocks, "page_map": page_map,
                "total_pages": total, "type": "pdf", "text_only": True}
    from tools.research_engine import extract_blocks
    blocks = extract_blocks(raw, mime)
    return {"blocks": blocks, "page_map": [None] * len(blocks),
            "total_pages": None, "type": "web", "text_only": True}


def page_cited_matches(claim_text: str, analysis: dict, *, matcher):
    """Cada fragmento conserva localizador físico para comparación editorial."""
    matches = matcher(claim_text, analysis["blocks"])
    results = []
    for match in matches:
        block_index = match["block_index"]
        page = analysis["page_map"][block_index]
        results.append({**match,
                        "page": page,
                        "locator": f"PDF página {page}" if page is not None else f"Bloque web {block_index + 1}"})
    return results

