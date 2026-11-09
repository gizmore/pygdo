"""Best-effort, opt-in exception notifications without local variables."""
import os
import smtplib
import socket
import ssl
import sys
import threading
import traceback
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr

_state = threading.local()


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

    # Do not include exception messages, source lines, request data, or locals:
    # they can contain SQL, credentials, tokens, or private conversation text.
    frames = traceback.extract_tb(error.__traceback__)
    stack = '\n'.join(f'  {frame.filename}:{frame.lineno} in {frame.name}' for frame in frames)
    body = (f'Time: {datetime.now(timezone.utc).isoformat()}\n'
            f'Host: {socket.gethostname()}\nPID: {os.getpid()}\n'
            f'Exception: {type(error).__module__}.{type(error).__qualname__}\n'
            f'Python: {sys.version.split()[0]}\n\nStack (no source or locals):\n{stack or "  unavailable"}\n')
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
