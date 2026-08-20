"""Stateless, short-lived approval tokens for linked connector accounts."""

import hashlib
import hmac

from gdo.base.Application import Application
from gdo.core.GDT_Token import GDT_Token
from gdo.date.Time import Time


class UserLinkToken:
    """Signs the two account IDs, an expiry and a random nonce with Core's pepper."""

    TTL = Time.ONE_MINUTE * 10

    @classmethod
    def create(cls, master, slave) -> str:
        nonce = GDT_Token.random()
        expires = int(Application.TIME + cls.TTL)
        payload = f'{master.get_id()}|{slave.get_id()}|{nonce}|{expires}'
        return f'{master.get_id()}.{slave.get_id()}.{nonce}.{expires}.{cls.signature(payload)}'

    @classmethod
    def parse(cls, token: str):
        try:
            master_id, slave_id, nonce, expires, signature = token.split('.')
            if not nonce or len(signature) != 64:
                return None
            master_id = int(master_id)
            slave_id = int(slave_id)
            expires = int(expires)
        except (TypeError, ValueError):
            return None
        if min(master_id, slave_id, expires) < 1 or expires < Application.TIME:
            return None
        payload = f'{master_id}|{slave_id}|{nonce}|{expires}'
        if not hmac.compare_digest(signature, cls.signature(payload)):
            return None
        return master_id, slave_id

    @staticmethod
    def signature(payload: str) -> str:
        from gdo.user.module_user import module_user
        pepper = module_user.instance().cfg_user_link_pepper().encode()
        return hmac.new(pepper, payload.encode(), hashlib.sha256).hexdigest()
