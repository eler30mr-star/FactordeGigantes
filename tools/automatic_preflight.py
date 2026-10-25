"""Read the owner's mode before legacy discovery. No search/provider invocation."""
import json
import os
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from tools.push_market_radar import HOST, github_oidc_token


def check(base_url, token, opener=urlopen):
    url = urlsplit(base_url)
    if (url.scheme != 'https' or url.netloc != HOST or url.path not in ('', '/')
            or url.query or url.fragment):
        raise ValueError('API_BASE_URL no corresponde al canal')
    request = Request(base_url.rstrip('/') + '/api/market/automation-control', headers={
        'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
    with opener(request, timeout=15) as response:
        data = json.loads(response.read(8193))
    if not isinstance(data, dict) or data.get('ok') is not True or not isinstance(data.get('allowed'), bool):
        raise ValueError('Estado del control no válido')
    # Old Wikimedia-first workflow is retired even if a future gate allows a
    # new YouTube workflow. Never resurrect this collector through a UI toggle.
    return {'allowed': False, 'automatic_enabled': data.get('automatic_enabled') is True,
            'reason': data.get('reason', 'legacy_discovery_retired')}


def main():
    result = check(os.environ.get('API_BASE_URL', ''), github_oidc_token())
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write('allowed=false\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
