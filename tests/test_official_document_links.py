"""Enlaces a documentos detectados en HTML corporativo, sin rastreo ni licencias."""
import unittest
from tools.official_document_links import find_official_document_links

URL="https://www.example.com/investors/index.html"

class OfficialLinksTests(unittest.TestCase):
    def test_press_releases_are_observed_links_and_not_an_ownership_attestation(self):
        result=find_official_document_links(URL,b'<a href="/newsroom/press-releases/2016/company-change">Company update</a><a href="/products">Products</a>')
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['url'],'https://www.example.com/newsroom/press-releases/2016/company-change')
        self.assertEqual(result[0]['category'],'corporate_news_link_candidate')
        self.assertFalse(result[0]['ownership_verified'])

    def test_find_pdf_and_annual_report_and_external_cdn_link(self):
        raw=b'''<html><body>
          <a href="/investors/reports/annual-report-2025.pdf">Annual Report 2025</a>
          <a href="https://cdn.example.org/reports/financial-statements.pdf">Financial Statements</a>
          <a href="https://www.example.com/investor-relations/">Investor Relations</a>
          <a href="/products">See phones</a>
          <a href="/investors/reports/annual-report-2025.pdf#page=4">Duplicated</a>
        </body></html>'''
        result=find_official_document_links(URL,raw)
        self.assertEqual(len(result),3)
        self.assertEqual(result[0]["category"],"financial_report_link_candidate")
        self.assertEqual(result[0]["url"],"https://www.example.com/investors/reports/annual-report-2025.pdf")
        self.assertTrue(result[0]["same_hostname_as_official_page"])
        self.assertTrue(result[1]["external_host_requires_independent_verification"])
        self.assertFalse(result[1]["ownership_verified"])
        self.assertFalse(any(x["facts_verified"] for x in result))
        self.assertFalse(any(x["document_fetched"] for x in result))

    def test_reject_unsafe_links_and_no_pdf_mime(self):
        raw=b'''<html><a href="javascript:alert(1)">Annual Report</a>
        <a href="http://127.0.0.1/report.pdf">Annual Report</a>
        <a href="http://example.com/report.pdf">Annual Report</a>
        <a href="/files/report.pdf">Report</a></html>'''
        result=find_official_document_links(URL,raw)
        self.assertEqual([x["url"] for x in result],["https://www.example.com/files/report.pdf"])
        self.assertEqual(find_official_document_links(URL,raw,mime="application/json"),[])

    def test_refuse_large_document_and_private_base(self):
        with self.assertRaises(ValueError):
            find_official_document_links(URL,b"x"*750001)
        with self.assertRaises(ValueError):
            find_official_document_links("https://127.0.0.1/home",b'<a href="/a.pdf">report</a>')

    def test_only_links_present_can_be_reported(self):
        raw=b"<html><p>Our annual report for 2025 will be published in due course.</p></html>"
        self.assertEqual(find_official_document_links(URL,raw),[])

if __name__=="__main__":
    unittest.main()

