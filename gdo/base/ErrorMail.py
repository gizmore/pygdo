"""Best-effort, opt-in exception notifications without local variables."""
import os
import re
import smtplib
import socket
import ssl
import sys
import threading
import traceback
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr
from urllib.parse import urlsplit

_state = threading.local()
_reported_lock = threading.Lock()


def install_async_exception_handler(loop):
    """Report unhandled task exceptions while preserving the loop's handler."""
    previous = loop.get_exception_handler()
    if getattr(previous, '_pygdo_error_mail_handler', False) is True:
        return

    def handler(active_loop, context):
        error = context.get('exception')
        if isinstance(error, Exception):
            try:
                from gdo.base.Logger import Logger
                Logger.exception(error, 'Unhandled asyncio task exception')
            except Exception:
                pass
        if previous:
            previous(active_loop, context)
        else:
            active_loop.default_exception_handler(context)

    handler._pygdo_error_mail_handler = True
    loop.set_exception_handler(handler)


def safe_stack(error):
    """Preserve chained exception locations without rendering values/locals."""
    entries, seen = [], set()
    current = error
    while current is not None and id(current) not in seen and len(entries) < 8:
        seen.add(id(current))
        frames = traceback.extract_tb(current.__traceback__)
        locations = '\n'.join(f'  {frame.filename}:{frame.lineno} in {frame.name}' for frame in frames)
        entries.append(f'{type(current).__module__}.{type(current).__qualname__}\n{locations or "  unavailable"}')
        current = current.__cause__ or (None if current.__suppress_context__ else current.__context__)
    return '\nCaused by / during handling:\n'.join(entries)


def request_context():
    """Return a redacted request route and identity, never URL parameters."""
    from gdo.base.Application import Application

    if not Application.IS_HTTP:
        return 'unavailable', 'unavailable'
    try:
        env = Application.STORAGE.environ
        uri = env.get('REQUEST_URI') or env.get('PATH_INFO') or env.get('path') or ''
        path = urlsplit(uri).path
        # PyGDO puts method arguments in dot-separated path segments as well as
        # queries. Keep only the route, never positional or named arguments.
        name = path.rsplit('/', 1)[-1]
        parts = name.split('.')
        prefix = path.rsplit('/', 1)[0]
        root = Application.web_root().rstrip('/')
        if (prefix == root and len(parts) >= 3 and
                all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', p) for p in parts[:2])):
            route = f'{prefix}/{parts[0]}.{parts[1]}.[redacted]'
        elif path == '/':
            route = '/'
        else:
            route = '[path redacted]'
        # Host is configured by the administrator, not taken from a Host header.
        domain = str(Application.domain())
        scheme = Application.PROTOCOL if Application.PROTOCOL in ('http', 'https') else ''
        url = f'{scheme}://{domain}{route}' if scheme and re.fullmatch(r'[A-Za-z0-9.:-]+', domain) else route
    except Exception:
        url = 'unavailable'
    try:
        user = Application.get_current_user()
        name = user.get_name() if user else None
        username = re.sub(r'[\x00-\x1f\x7f]', '', str(name))[:192] if name else 'unavailable'
    except Exception:
        username = 'unavailable'
    return url, username


def report_exception(error):
    from gdo.base.Application import Application

    if getattr(_state, 'sending', False):
        return False
    target = Application.config('mail.errors_to', '')
    if not isinstance(target, str) or not target.strip():
        return False
    if '\n' in target or '\r' in target:
        return False
    recipients = [address for _, address in getaddresses([target]) if address and '@' in address]
    if not recipients or str(Application.config('mail.debug', '1')) != '0':
        return False

    # The same exception can be logged at several stack boundaries (for
    # example ASGI plus its error renderer). Attempt at most one email per
    # exception object; never retry via a nested logging failure.
    with _reported_lock:
        if getattr(error, '_pygdo_error_mail_reported', False):
            return False
        try:
            error._pygdo_error_mail_reported = True
        except (AttributeError, TypeError):
            # Unusual immutable exception types cannot carry the marker.
            pass

    # Do not include exception messages, source lines, URL arguments, or locals:
    # they can contain SQL, credentials, tokens, or private conversation text.
    stack = safe_stack(error)
    url, username = request_context()
    body = (f'Time: {datetime.now(timezone.utc).isoformat()}\n'
            f'Host: {socket.gethostname()}\nPID: {os.getpid()}\n'
            f'URL: {url}\nUser: {username}\n'
            f'Exception: {type(error).__module__}.{type(error).__qualname__}\n'
            f'Python: {sys.version.split()[0]}\n\nStack (no source or locals):\n{stack}\n')
    try:
        _state.sending = True
        sender = parseaddr(str(Application.config('mail.sender', '')))[1]
        if not sender or '@' not in sender:
            return False
        message = EmailMessage()
        message['From'] = sender
        message['To'] = ', '.join(recipients)
        message['Subject'] = f'PyGDO exception: {type(error).__name__}'
        message.set_content(body)
        host = Application.config('mail.host', 'localhost')
        port = int(Application.config('mail.port', 587))
        with smtplib.SMTP(host, port, timeout=5) as server:
            if str(Application.config('mail.tls', '1')) == '1':
                server.starttls(context=ssl.create_default_context())
            login = Application.config('mail.user', '')
            if login:
                server.login(login, Application.config('mail.pass', ''))
            server.send_message(message, from_addr=sender, to_addrs=recipients)
        return True
    except Exception as mail_error:
        # Never call Logger.exception here: failures must not mail themselves.
        sys.stderr.write(f'Error-mail delivery failed ({type(mail_error).__name__}).\n')
        return False
    finally:
        _state.sending = False
