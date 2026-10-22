import unittest
from tools.ai_clients import MODELS, FreeClients, ProviderError

class FreeModelGate(unittest.TestCase):
    def test_models_on_confirmed_free_tier(self):
        self.assertEqual(MODELS["gemini"], "gemini-3.5-flash-lite")
        self.assertEqual(MODELS["groq"], "openai/gpt-oss-120b")
        self.assertNotIn("gemini-3.8-flash", MODELS.values())

    def test_single_inference_per_provider_even_when_enabled(self):
        calls=[]
        def response(url,body,headers):
            calls.append((url,body))
            if "googleapis.com" in url:
                self.assertIn("gemini-3.5-flash-lite",url)
                return {"candidates":[{"content":{"parts":[{"text":"{}"}]}}]}
            self.assertEqual(body["model"],"openai/gpt-oss-120b")
            return {"choices":[{"message":{"content":"{}"}}]}
        env={"GEMINI_API_KEY":"test-fixture","GEMINI_RESEARCH_FREE_CONFIRMED":"1",
             "GROQ_API_KEY":"test-fixture","GROQ_RESEARCH_FREE_CONFIRMED":"1"}
        c=FreeClients(env=env,reserve=lambda *_:True,transport=response)
        c.generate("gemini","Solicitud de prueba")
        c.generate("groq","Solicitud de prueba")
        with self.assertRaises(ProviderError):c.generate("gemini","Una segunda solicitud")
        with self.assertRaises(ProviderError):c.generate("groq","Una segunda solicitud")
        self.assertEqual(len(calls),2)

if __name__=="__main__":unittest.main()
