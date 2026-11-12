"""Small shared HMAC protocol for independently deployed challenge services."""
import base64
import binascii
import hashlib
import hmac
import os
import pwd
import re
from pathlib import Path


def bj_secret_path():
    """Keep shared credentials outside the web tree; allow deployment overrides."""
    if configured := os.environ.get('PYGDO_BJ_SECRET_PATH'):
        return Path(configured)
    app_root = Path(__file__).resolve().parents[2]
    owner_home = Path(pwd.getpwuid(app_root.stat().st_uid).pw_dir)
    return owner_home / '.config' / 'pygdo' / 'secret_bj_token'


def read_secret(path):
    secret = Path(path).read_bytes().strip()
    if not re.fullmatch(rb'[0-9a-f]{64}', secret):
        raise ValueError('Challenge token secret is not configured')
    return bytes.fromhex(secret.decode('ascii'))


def issue(secret, context, subject):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError('Challenge token secret is invalid')
    if not isinstance(context, str) or not re.fullmatch(r'[a-z][a-z0-9]{0,15}', context):
        raise ValueError('Challenge token context is invalid')
    if not isinstance(subject, str) or not subject or len(subject.encode('utf-8')) > 256:
        raise ValueError('Challenge token subject is invalid')
    encoded = base64.urlsafe_b64encode(subject.encode('utf-8')).rstrip(b'=').decode('ascii')
    message = f'{context}.{encoded}'
    signature = hmac.new(secret, message.encode('ascii'), hashlib.sha256).hexdigest()
    return f'{message}.{signature}'


def verify(secret, context, token):
    if not isinstance(token, str) or len(token) > 512:
        return False
    parts = token.split('.')
    if len(parts) != 3 or parts[0] != context or not re.fullmatch(r'[A-Za-z0-9_-]{1,342}', parts[1]) or not re.fullmatch(r'[0-9a-f]{64}', parts[2]):
        return False
    try:
        subject = base64.b64decode(parts[1] + '=' * (-len(parts[1]) % 4), altchars=b'-_', validate=True).decode('utf-8')
        expected = issue(secret, context, subject)
    except (ValueError, UnicodeError, binascii.Error):
        return False
    return hmac.compare_digest(expected, token)
