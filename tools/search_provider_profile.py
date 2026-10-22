"""Lectura del plan Tavily, sin búsquedas, facturación ni claves en la salida."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,build_opener
from tools.ai_clients import NoRedirects,ProviderError


def read_tavily_usage(key):
    request=Request('https://api.tavily.com/usage',method='GET',headers={
        'Authorization':'Bearer '+key,'Accept':'application/json',
        'User-Agent':'FactorDeGigantesResearch/2.0'})
    try:
        with build_opener(NoRedirects()).open(request,timeout=15) as response:
            raw=response.read(16001)
            if len(raw)>16000:raise ProviderError('profile_too_large')
            data=json.loads(raw)
            if not isinstance(data,dict):raise ProviderError('invalid_profile')
            return data
    except HTTPError as exc:
        raise ProviderError('profile_credentials_rejected' if exc.code in (401,403) else 'profile_unavailable',exc.code) from None
    except (URLError,OSError,TimeoutError,ValueError,UnicodeError):
        raise ProviderError('profile_unavailable') from None


def assess_tavily_usage(data,*,paygo_disabled_confirmed=False):
    if not isinstance(data,dict):raise ValueError('Perfil inválido')
    account,key=data.get('account'),data.get('key')
    if not isinstance(account,dict) or not isinstance(key,dict):raise ValueError('Perfil incompleto')
    plan=account.get('current_plan')
    fields=['plan_usage','plan_limit','paygo_usage','paygo_limit']
    def integer(value):
        if type(value) is int and value>=0:return value
        if type(value) is float and value>=0 and value.is_integer():return int(value)
        if isinstance(value,str) and value.isascii() and value.isdigit() and len(value)<=9:return int(value)
        raise ValueError('Límite numérico no verificable')
    owner_confirmed_null=(account.get('paygo_limit') is None and paygo_disabled_confirmed is True)
    account={**account,**{k:(None if k=='paygo_limit' and owner_confirmed_null else integer(account.get(k))) for k in fields}}
    if not isinstance(plan,str) or len(plan)>40:
        raise ValueError('Plan sin límites comprobables')
    usage=integer(key.get('usage'))
    limit=None if key.get('limit') is None else integer(key['limit'])
    free=(plan.lower() in ('researcher','free') and account['plan_limit']==1000 and
          account['paygo_usage']==0 and (account['paygo_limit']==0 or owner_confirmed_null) and
          account['plan_usage']+2<=account['plan_limit'] and (limit is None or usage+2<=limit))
    return {'provider':'tavily','status':('owner_confirmed_no_paygo' if owner_confirmed_null else 'verified_free_no_paygo') if free else 'free_profile_not_confirmed',
            'free_search_confirmed':free,'plan':plan,
            'paygo_confirmation_source':'owner' if owner_confirmed_null else 'usage_api',
            **{k:account[k] for k in fields},'key_usage':usage,'key_limit':limit,
            'searches_executed':0,'billing_changed':False}


def check_tavily_profile(env=None,*,fetcher=read_tavily_usage):
    env=os.environ if env is None else env
    base={'provider':'tavily','free_search_confirmed':False,'searches_executed':0,'billing_changed':False}
    if env.get('TAVILY_RESEARCH_FREE_CONFIRMED')=='0':return {**base,'status':'disabled'}
    key=env.get('TAVILY_API_KEY','').strip()
    if not key:return {**base,'status':'missing_key'}
    data=None
    try:
        data=fetcher(key)
        return assess_tavily_usage(data,paygo_disabled_confirmed=env.get('TAVILY_RESEARCH_FREE_CONFIRMED')=='1')
    except ProviderError as exc:return {**base,'status':exc.code}
    except (ValueError,TypeError,KeyError):
        account=data.get('account') if isinstance(data,dict) else None
        key_data=data.get('key') if isinstance(data,dict) else None
        fields=['current_plan','plan_usage','plan_limit','paygo_usage','paygo_limit']
        observed={k:type(account.get(k)).__name__ for k in fields} if isinstance(account,dict) else {}
        key_types={k:type(key_data.get(k)).__name__ for k in ('usage','limit')} if isinstance(key_data,dict) else {}
        known_plans={'researcher','free','bootstrap','startup','growth','project','enterprise','pay as you go'}
        plan=account.get('current_plan') if isinstance(account,dict) else None
        return {**base,'status':'invalid_profile','plan':plan if isinstance(plan,str) and plan.lower() in known_plans else 'unrecognized',
                'account_field_types':observed,'key_field_types':key_types}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=check_tavily_profile()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('TAVILY_PROFILE:',json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
