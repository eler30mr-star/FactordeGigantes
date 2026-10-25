import io
import json
import unittest
from tools.automatic_preflight import check
from tools.push_market_radar import HOST


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AutomaticPreflightTests(unittest.TestCase):
    def test_off_does_not_allow_legacy_discovery(self):
        def opener(request, timeout):
            self.assertEqual(request.full_url, 'https://' + HOST + '/api/market/automation-control')
            self.assertEqual(request.get_header('Authorization'), 'Bearer ephemeral-token')
            return Response(json.dumps({'ok': True, 'allowed': False,
                'automatic_enabled': False, 'reason': 'automatic_off'}).encode())
        self.assertFalse(check('https://' + HOST, 'ephemeral-token', opener)['allowed'])

    def test_future_selector_cannot_reactivate_old_collector(self):
        def opener(*args, **kwargs):
            return Response(b'{"ok":true,"allowed":true,"automatic_enabled":true}')
        result = check('https://' + HOST, 'ephemeral-token', opener)
        self.assertFalse(result['allowed'])
        self.assertTrue(result['automatic_enabled'])

    def test_invalid_url_rejected_before_network(self):
        for url in ('http://' + HOST, 'https://evil.test', 'https://' + HOST + '/api',
                    'https://' + HOST + '?secret=x', 'https://user@' + HOST):
            with self.assertRaises(ValueError):
                check(url, 'ephemeral-token', lambda *a, **k: self.fail('network forbidden'))

    def test_error_or_unknown_mode_never_allows_discovery(self):
        for body in (b'{}', b'{"ok":true}', b'{"ok":true,"allowed":"true"}', b'{"ok":false,"allowed":true}'):
            with self.assertRaises(ValueError):
                check('https://' + HOST, 'ephemeral-token', lambda *a, **k: Response(body))
