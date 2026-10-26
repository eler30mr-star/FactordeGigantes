"""Bounded reviewer availability fallback; model output is still unverified."""
from tools.ai_clients import ProviderError


class ReviewProviderUnavailable(ProviderError):
    def __init__(self, reason, attempts):
        super().__init__(reason)
        self.attempts = attempts


def generate_support_review(clients, prompt):
    attempts = []
    for provider in ('groq', 'gemini'):
        try:
            options = {'max_output_tokens': 3200}
            if provider == 'gemini': options['role'] = 'review'
            raw, metadata = clients.generate(provider, prompt, **options)
            return raw, metadata, provider, attempts
        except ProviderError as exc:
            attempts.append({'provider': provider, 'role': 'review', 'status': exc.code})
            if exc.code not in {'missing_key', 'free_mode_unconfirmed', 'budget_denied', 'quota_exhausted',
                    'credentials_rejected', 'network_failure', 'provider_stopped', 'run_budget_exhausted'}:
                break
    raise ReviewProviderUnavailable(attempts[0]['status'], attempts)
