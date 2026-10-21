"""Extraer enlaces a informes originales de HTML corporativo YA descargado.

No rastrea internet, no adivina URLs, no sigue enlaces. La mención y el enlace
no implican autenticidad, propiedad, derechos comerciales ni verdad del dato.
"""
from __future__ import annotations
from html.parser import HTMLParser
from html import unescape
from urllib.parse import urljoin, urldefrag, urlsplit
import re

from tools.research_engine import validate_url

MAX_LINKS=250
MAX_CANDIDATES=12
MAX_HTML=750_000
REPORT_TERMS=(
    "annual report","annual-report","annual_report","integrated report",
    "annual financial","financial statements","financial report",
    "form 10-k","10-k","20-f","informe anual","informes anuales",
    "estados financieros","reporte anual","memoria anual"
)
IR_TERMS=("investor relations","investors","inversores","inversionistas","financial results")

class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.current=None
        self.links=[]

    def handle_starttag(self,tag,attrs):
        if tag!="a":
            return
        attrs=dict(attrs)
        href=attrs.get("href")
        if isinstance(href,str) and 0<len(href)<=1000 and len(self.links)<MAX_LINKS:
            self.current=[href,[]]

    def handle_data(self,data):
        if self.current is not None and sum(len(x) for x in self.current[1])<220:
            self.current[1].append(data[:220])

    def handle_endtag(self,tag):
        if tag=="a" and self.current is not None:
            href,parts=self.current
            self.links.append((href," ".join(parts)[:180]))
            self.current=None


def find_official_document_links(page_url, html_bytes, *, mime="text/html"):
    validate_url(page_url)
    if not isinstance(html_bytes,bytes) or len(html_bytes)>MAX_HTML:
        raise ValueError("HTML fuera de límite")
    if "html" not in mime.lower():
        return []
    parser=Links()
    parser.feed(html_bytes.decode("utf-8",errors="replace"))
    parser.close()
    base=urlsplit(page_url).hostname.lower()
    candidates=[]
    seen=set()
    for href,text in parser.links:
        raw=unescape(href).strip()
        if not raw or raw.startswith(("#","javascript:","data:","mailto:")):
            continue
        try:
            url=urldefrag(urljoin(page_url,raw))[0]
            validate_url(url)
        except (ValueError,OverflowError):
            continue
        if url in seen:
            continue
        p=urlsplit(url)
        label=" ".join((text+" "+p.path.replace("_"," ").replace("-"," ")).lower().split())
        pdf=p.path.lower().endswith(".pdf")
        is_report=any(term in label for term in REPORT_TERMS)
        is_ir=any(term in label for term in IR_TERMS)
        if not (pdf or is_report or is_ir):
            continue
        seen.add(url)
        host=p.hostname.lower()
        candidates.append({
            "url":url,
            "anchor_text":re.sub(r"\s+"," ",text).strip()[:140],
            "category":"financial_report_link_candidate" if is_report else
                       "pdf_link_candidate" if pdf else "investor_information_page_candidate",
            "pdf_by_filename":pdf,
            "same_hostname_as_official_page":host==base,
            "external_host_requires_independent_verification":host!=base,
            "document_fetched":False,
            "ownership_verified":False,
            "facts_verified":0,
            "commercial_rights_verified":False
        })
        if len(candidates)>=MAX_CANDIDATES:
            break
    return candidates
