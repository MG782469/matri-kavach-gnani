"""Explicit, synthetic-only public demonstration mode.

By default it is protected by one shared demo password (HTTP Basic). With DEMO_OPEN=1
it is open to anyone, for judges; it is still mock-only, fictional data, no Gnani key.
Not clinical auth; never suitable for real patient information.
"""
import base64
import hmac
import os


def public_mode():
    return os.getenv('DEMO_PUBLIC', '0').strip() == '1'


def open_mode():
    """Public preview without the shared password (still mock-only and synthetic-only)."""
    return public_mode() and os.getenv('DEMO_OPEN', '0').strip() == '1'


def validate_public_config():
    if not public_mode():
        return
    if os.getenv('GNANI_MODE', 'mock').strip().lower() != 'mock':
        raise ValueError('Public demo must run in GNANI_MODE=mock; live Gnani credits are private-only')
    password = os.getenv('DEMO_ACCESS_PASSWORD', '')
    if not open_mode() and len(password) < 16 or password.lower() in {'changemechangeme', 'passwordpassword'}:
        raise ValueError('Public demo requires a unique DEMO_ACCESS_PASSWORD of 16+ characters')
    if os.getenv('REFERRAL_BACKEND_URL'):
        raise ValueError('Public demo must not configure REFERRAL_BACKEND_URL')


def correct_basic_auth(value):
    if not public_mode() or open_mode():
        return True
    if not isinstance(value, str) or not value.startswith('Basic '):
        return False
    try:
        payload = base64.b64decode(value[6:], validate=True).decode('utf-8')
        username, password = payload.split(':', 1)
    except (ValueError, UnicodeError):
        return False
    return hmac.compare_digest(username, 'demo') and hmac.compare_digest(password, os.getenv('DEMO_ACCESS_PASSWORD',''))
