"""Ensayos SEC XBRL sin red: identidad, cifras, periodos y revisiones."""
import json
from pathlib import Path
import tempfile
import unittest
from tools import financial_facts as f
from tools import financial_probe as probe

CIK="0000320193"
URL=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

def filing(value, start="2024-09-29",end="2025-09-27",form="10-K",
           accn="0000320193-25-000079",filed="2025-10-31",fp="FY",fy=2025):
    return {"start":start,"end":end,"val":value,"form":form,
            "accn":accn,"filed":filed,"fp":fp,"fy":fy}

def document():
    return {"cik":320193,"entityName":"Apple Inc.","facts":{"us-gaap":{
        "RevenueFromContractWithCustomerExcludingAssessedTax":{
            "units":{"USD":[
                filing(400_000_000_000),
                filing(400_000_000_000,accn="0000320193-25-000082",filed="2025-11-05"),
                filing(399_000_000_000,accn="0000320193-25-000096",filed="2025-12-01"),
                filing(390_000_000_000,start="2023-10-01",end="2024-09-28",accn="0000320193-24-000123",filed="2024-11-01",fy=2024),
                filing(77_000_000_000,start="2025-06-29",end="2025-09-27",accn="0000320193-25-000101",filed="2025-11-11",form="10-Q",fp="Q4"),
            ]}},
        "Assets":{"units":{"USD":[
            {"end":"2025-09-27","val":350_000_000_000,"form":"10-K",
             "accn":"0000320193-25-000079","filed":"2025-10-31","fp":"FY","fy":2025},
            {"end":"2024-09-28","val":340_000_000_000,"form":"10-K",
             "accn":"0000320193-24-000123","filed":"2024-11-01","fp":"FY","fy":2024}
        ]}},
        "RiskFreeInterestRate":{"units":{"pure":[filing(0.75)]}},
    }}}

class FinancialFactsTests(unittest.TestCase):
    def test_parse_xbrl_retains_cik_metric_units_dates_and_provenance(self):
        raw=json.dumps(document()).encode()
        result=f.analyze_companyfacts(raw,source_url=URL)
        self.assertEqual(result["entity_cik"],CIK)
        self.assertEqual(result["entity_name_reported"],"Apple Inc.")
        self.assertEqual(result["observation_count"],7)
        self.assertEqual(result["facts_automatically_verified"],0)
        self.assertFalse(result["ready_for_documentary"])
        self.assertEqual(len(result["content_sha256"]),64)

    def test_only_same_metric_currency_period_and_entity_compared(self):
        observations=f.extract_observations(document(),document_url=URL)
        diff=f.compare_observations(observations)
        self.assertEqual(diff["same_period_differences"],1)
        result=diff["comparisons"][0]
        self.assertEqual(result["entity_cik"],CIK)
        self.assertEqual(result["start"],"2024-09-29")
        self.assertEqual(result["end"],"2025-09-27")
        self.assertEqual(result["metric"],"RevenueFromContractWithCustomerExcludingAssessedTax")
        self.assertEqual(result["unit"],"USD")
        self.assertEqual(result["distinct_values"],["399000000000","400000000000"])
        self.assertFalse(result["proven_contradiction"])
        self.assertFalse(result["fraud_claim"])
        self.assertEqual(diff["confirmed_contradictions"],0)

    def test_different_year_or_period_must_not_be_called_conflicting(self):
        obs=f.extract_observations(document(),document_url=URL)
        obs=[o for o in obs if o["accession"]!="0000320193-25-000096"]
        r=f.compare_observations(obs)
        self.assertEqual(r["same_period_differences"],0)

    def test_reject_fake_sec_host_and_cik_mismatch(self):
        data=document()
        for url in ["https://other.com/CIK0000320193.json",
                    "https://data.sec.gov.evil.example/api/xbrl/companyfacts/CIK0000320193.json",
                    "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json"]:
            with self.assertRaises(ValueError):
                f.extract_observations(data,document_url=url)
        obs=f.extract_observations(data,document_url=URL)
        obs[0]["source_url"]="https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json"
        with self.assertRaises(ValueError):
            f.compare_observations(obs)

    def test_malformed_numbers_and_flags_are_rejected_or_skipped(self):
        for val in [True,"NaN","1e400","+4","1,000",float("inf"),None,"3.23456789123"]:
            with self.assertRaises(ValueError):
                f.decimal_value(val)
        data=document()
        data["facts"]["us-gaap"]["Assets"]["units"]["USD"][0]["val"]="NaN"
        r=f.extract_observations(data,document_url=URL)
        self.assertEqual(len(r),6)

    def test_unnamed_or_missing_data_never_fabricates_values(self):
        empty={"cik":320193,"entityName":"Apple Inc.","facts":{"us-gaap":{}}}
        r=f.analyze_companyfacts(json.dumps(empty).encode(),source_url=URL)
        self.assertEqual(r["observation_count"],0)
        self.assertEqual(r["comparison"]["same_period_differences"],0)

    def test_fetch_rejects_wrong_content_type_or_redirect_or_size(self):
        raw=json.dumps(document()).encode()
        def fetcher(url):
            self.assertEqual(url,URL)
            return raw,url,"application/json"
        data,url=f.fetch_companyfacts("320193",fetcher=fetcher)
        self.assertEqual(url,URL)
        self.assertEqual(data,raw)
        with self.assertRaises(ValueError):
            f.fetch_companyfacts(CIK,fetcher=lambda url:(raw,"https://example.org/document","application/json"))
        with self.assertRaises(ValueError):
            f.fetch_companyfacts(CIK,fetcher=lambda url:(raw,url,"text/html"))
        with self.assertRaises(ValueError):
            f.fetch_companyfacts(CIK,fetcher=lambda url:(b"x"*(f.MAX_JSON_BYTES+1),url,"application/json"))

    def test_cli_offline_writes_json_without_rights_and_render(self):
        with tempfile.TemporaryDirectory() as temp:
            obj=document()
            raw=json.dumps(obj).encode()
            report=f.analyze_companyfacts(raw,source_url=URL)
            self.assertFalse(report["rights_verified"])
            self.assertEqual(report["comparison"]["facts_human_verified"],0)
            filepath=Path(temp)/"fixture.json"
            filepath.write_bytes(raw)
            self.assertEqual(report["observations"][0]["source_url"],URL)

    def test_automatic_candidate_probe_stays_unapproved_even_when_readable(self):
        data=json.dumps(document()).encode()
        report={"entities":[{"cik_candidate":CIK,"status":"sec_filings_listed"}]}
        result=probe.probe_candidates(report,fetcher=lambda url:(data,url,"application/json"))
        self.assertEqual(result["status"],"retrieved_structured_candidates")
        self.assertEqual(result["analysis"]["observation_count"],7)
        self.assertEqual(result["analysis"]["comparison"]["same_period_differences"],1)
        self.assertFalse(result["identity_verified"])
        self.assertFalse(result["publication_authorized"])

    def test_companyfacts_blocked_and_no_cik_do_not_invent_data(self):
        report={"entities":[{"cik_candidate":CIK}]}
        result=probe.probe_candidates(report,fetcher=lambda _: (_ for _ in ()).throw(OSError("SEC blocked")))
        self.assertEqual(result["status"],"sec_unavailable_or_unreadable")
        self.assertIsNone(result["analysis"])
        self.assertEqual(result["error_type"],"OSError")
        missing=probe.probe_candidates({"entities":[{"cik_candidate":None}]})
        self.assertEqual(missing["status"],"no_identifier")
        self.assertEqual(missing["facts_verified_automatically"],0)

if __name__=="__main__":
    unittest.main()
