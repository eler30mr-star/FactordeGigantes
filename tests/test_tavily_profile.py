import copy,unittest
from tools.search_provider_profile import assess_tavily_usage,check_tavily_profile

def profile():
    return {'account':{'current_plan':'Researcher','plan_usage':0,'plan_limit':1000,
                       'paygo_usage':0,'paygo_limit':0},'key':{'usage':0,'limit':None}}

class TavilyProfileTests(unittest.TestCase):
    def test_free_no_paygo_and_remaining_credits_are_required(self):
        self.assertTrue(assess_tavily_usage(profile())['free_search_confirmed'])
        for change in (lambda d:d['account'].update(current_plan='Bootstrap'),
                       lambda d:d['account'].update(paygo_limit=1),
                       lambda d:d['account'].update(paygo_usage=1),
                       lambda d:d['account'].update(plan_limit=15000),
                       lambda d:d['account'].update(plan_usage=999),
                       lambda d:d['key'].update(limit=1)):
            data=profile();change(data)
            self.assertFalse(assess_tavily_usage(data)['free_search_confirmed'])

    def test_explicit_off_or_missing_key_never_accesses_service(self):
        for env in ({},{'TAVILY_API_KEY':'fixture','TAVILY_RESEARCH_FREE_CONFIRMED':'0'}):
            self.assertFalse(check_tavily_profile(env,fetcher=lambda _:self.fail('No consultar'))['free_search_confirmed'])

    def test_only_whitelisted_plan_fields_leave_the_checker(self):
        data=profile();data['secret']='must-not-leave';data['account']['email']='private@example.test'
        result=check_tavily_profile({'TAVILY_API_KEY':'fixture'},fetcher=lambda _:data)
        self.assertNotIn('must-not-leave',str(result));self.assertNotIn('private@example.test',str(result))
        self.assertEqual(result['searches_executed'],0)

    def test_malformed_plan_cannot_enable_search(self):
        for data in ({},[],{'account':{},'key':{}}):
            result=check_tavily_profile({'TAVILY_API_KEY':'fixture'},fetcher=lambda _:data)
            self.assertFalse(result['free_search_confirmed'])

    def test_integer_counters_can_be_encoded_as_numbers_or_decimal_strings(self):
        data=profile();data['account']['paygo_limit']=0.0;data['account']['plan_usage']='0'
        self.assertTrue(assess_tavily_usage(data)['free_search_confirmed'])
        data['account']['paygo_limit']=None
        result=check_tavily_profile({'TAVILY_API_KEY':'fixture'},fetcher=lambda _:data)
        self.assertFalse(result['free_search_confirmed'])
        self.assertEqual(result['account_field_types']['paygo_limit'],'NoneType')

if __name__=='__main__':unittest.main()
