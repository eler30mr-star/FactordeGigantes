"""Contratos offline: noticias RSS de prueba NO representan titulares actuales."""
import unittest
from datetime import datetime,timezone,timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape
from tools.news_discovery import discover_news,parse_news_rss,news_feed_url

NOW=datetime(2026,10,21,19,0,tzinfo=timezone.utc)

def rss(title="Empresa presenta innovación de una tecnología industrial",source="Medio de ejemplo",
        link="https://news.google.com/rss/articles/CBMiFAKE",hours=5):
    stamp=format_datetime(NOW-timedelta(hours=hours))
    return (f'<rss version="2.0"><channel><item><title>{escape(title)}</title>'
            f'<link>{escape(link)}</link><source>{escape(source)}</source>'
            f'<pubDate>{stamp}</pubDate></item></channel></rss>').encode()

class NewsDiscoveryTests(unittest.TestCase):
    def test_titulares_se_conservan_sin_verificacion(self):
        items=parse_news_rss(rss(),"innovacion",now=NOW)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["verification_state"],"unverified")
        self.assertFalse(items[0]["youtube_demand_verified"])
        self.assertFalse(items[0]["editorial_authorized"])
        self.assertEqual(items[0]["source_label"],"Medio de ejemplo")

    def test_fuentes_inadecuadas_y_antiguas_se_descartan(self):
        self.assertEqual(parse_news_rss(rss(link="http://127.0.0.1/private"),"empresas",now=NOW),[])
        self.assertEqual(parse_news_rss(rss(hours=80),"empresas",now=NOW),[])
        self.assertEqual(parse_news_rss(rss(link="https://news.google.com.evil.test/rss/articles/fake"),
                                       "empresas",now=NOW),[])
        with self.assertRaises(ValueError):
            parse_news_rss(b'<!DOCTYPE rss [ <!ENTITY x "x"> ]><rss/>',"empresas",now=NOW)

    def test_no_nombres_plantados_y_dedupe_real(self):
        calls=[]
        def fake(url):
            calls.append(url)
            return rss()
        data=discover_news(now=NOW,fetch=fake)
        self.assertEqual(len(calls),4)
        self.assertTrue(all("Theranos" not in url for url in calls))
        self.assertEqual(data["lead_count"],1)
        self.assertEqual(data["feeds_succeeded"],4)
        self.assertFalse(data["market_study_complete"])
        self.assertFalse(data["ready_for_youtube"])
        self.assertEqual(len(data["feeds"]),4)

    def test_todos_los_feeds_caidos_fallan_sin_simular_datos(self):
        with self.assertRaises(RuntimeError):
            discover_news(now=NOW,fetch=lambda u:(_ for _ in ()).throw(OSError("sin red")))
        url=news_feed_url("es","PE","industria")
        self.assertIn("news.google.com/rss/search?",url)

if __name__=="__main__":
    unittest.main()
