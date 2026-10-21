"""PDF: descarga acotada, texto por página y cero aprobación editorial.

Se fabrica un PDF mínimo de dos páginas con la librería estándar: el test
no descarga informes externos, no necesita reportlab ni imágenes.
"""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import pdf_sources, research_engine

ROOT=Path(__file__).resolve().parents[1]
DOSSIER=json.loads((ROOT/"research/blackberry/expediente_preliminar.json").read_text(encoding="utf-8"))
PDF_URL="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"


def two_page_pdf():
    paragraphs=[
        "Research In Motion: this is a heading without the date of foundation.",
        "Research In Motion was founded in 1984 by Mike Lazaridis and Douglas Fregin.",
    ]
    objs=[
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 6 0 R >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 7 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for paragraph in paragraphs:
        stream=f"BT /F1 12 Tf 72 720 Td ({paragraph}) Tj ET".encode("ascii")
        objs.append("<< /Length "+str(len(stream))+" >>\nstream\n"+stream.decode()+"\nendstream")
    data=bytearray(b"%PDF-1.4\n")
    offsets=[0]
    for number, obj in enumerate(objs, 1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n{obj}\nendobj\n".encode())
    xref=len(data)
    data.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(data)


class PdfEvidenceTests(unittest.TestCase):
    def test_pdf_text_and_actual_page_number(self):
        raw=two_page_pdf()
        blocks,page_map,total=pdf_sources.pdf_page_blocks(raw)
        self.assertEqual(total,2)
        self.assertIn(2,page_map)
        self.assertTrue(any("1984" in b for b in blocks))
        analysis=pdf_sources.analyze_document(raw,"application/pdf")
        found=pdf_sources.page_cited_matches(
            "Research In Motion was founded in 1984 by Mike Lazaridis",
            analysis,matcher=research_engine.excerpts_for_claim)
        self.assertTrue(any(e["page"]==2 for e in found))
        self.assertTrue(all(e["verification_status"]=="candidate_unchecked" for e in found))
        self.assertTrue(all("PDF página" in e["locator"] for e in found))

    def test_real_dossier_with_pdf_keeps_page_and_pending_state(self):
        dossier=copy.deepcopy(DOSSIER)
        dossier["sources"][0]["url"]=PDF_URL
        original=copy.deepcopy(dossier)
        raw=two_page_pdf()
        def fetch(url):
            if url==PDF_URL:return raw,url,"application/pdf"
            return b"<html><body><p>La empresa mostró una transición tecnológica sin declarar cifras.</p></body></html>",url,"text/html"
        result=research_engine.research_dossier(dossier,fetcher=fetch,max_requests=2)
        self.assertEqual(result["sources"][0]["document_type"],"pdf")
        self.assertEqual(result["sources"][0]["pdf_total_pages"],2)
        self.assertTrue(any(c["page"]==2 for c in result["candidate_claims"][0]["candidate_passages"]))
        self.assertFalse(result["production_ready"])
        self.assertEqual(result["facts_verified_automatically"],0)
        self.assertEqual(result["rights_verified_automatically"],0)
        self.assertEqual(dossier,original)
        context=research_engine.assemble_ai_evidence(result)
        self.assertIn("PDF página 2",context)

    def test_reject_non_pdf_overlong_or_invalid(self):
        with self.assertRaises(ValueError):
            pdf_sources.pdf_page_blocks(b"not a pdf")
        with self.assertRaises(ValueError):
            pdf_sources.pdf_page_blocks(b"%PDF-"+b"x"*pdf_sources.MAX_PDF_BYTES)
        with self.assertRaises(ValueError):
            pdf_sources.pdf_page_blocks(b"%PDF-1.4\ncorrupt")
        one_page=two_page_pdf()
        with patch.object(pdf_sources,"MAX_PDF_PAGES",1):
            with self.assertRaisesRegex(ValueError,"páginas"):
                pdf_sources.pdf_page_blocks(one_page)

    def test_html_keeps_compatibility_without_fake_page(self):
        analysis=pdf_sources.analyze_document(
            b"<html><body><p>This is a sufficiently long text about corporate business and financial history.</p></body></html>",
            "text/html")
        self.assertEqual(analysis["type"],"web")
        self.assertEqual(analysis["page_map"],[None])
        self.assertIsNone(analysis["total_pages"])
        found=pdf_sources.page_cited_matches(
            "Corporate business financial history",analysis,matcher=research_engine.excerpts_for_claim)
        self.assertTrue(found)
        self.assertEqual(found[0]["locator"],"Bloque web 1")
        self.assertIsNone(found[0]["page"])


if __name__=="__main__":
    unittest.main()
