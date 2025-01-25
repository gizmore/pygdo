from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Token import GDT_Token
from gdo.form.GDT_Hidden import GDT_Hidden


class GDT_CSRF(GDT_Hidden):
    TOKEN_LEN = 12
    MAX_TOKENS = 17
    MAX_TOKENS_GHOST = 256

    @staticmethod
    def get_storage(user: GDO_User):
        return Cache.get('csrf', user.get_id(), [])

    @staticmethod
    def set_storage(storage: list[str], user: GDO_User|None):
       Cache.set('csrf', user.get_id(), storage)

    def __init__(self, name='csrf'):
        super().__init__(name)
        self.not_null()

    def render_cli(self) -> str:
        return ''

    def render_form(self):
        self.val(self.generate_token())
        return super().render_form()

    def generate_token(self) -> str:
        token = GDT_Token.random(self.TOKEN_LEN)
        user = GDO_User.current()
        tokens = GDT_CSRF.get_storage(user)
        tokens.append(token)
        max = self.MAX_TOKENS if user.is_persisted() else self.MAX_TOKENS_GHOST
        if len(tokens) > max:
            tokens = tokens[-max:]
        GDT_CSRF.set_storage(tokens, user)
        return token

    def validate(self, val: str | None, value: any) -> bool:
        if Application.is_unit_test():
            return True
        user = GDO_User.current()
        tokens = GDT_CSRF.get_storage(user)
        if value not in tokens:
            return self.error('err_csrf')
        tokens.remove(value)
        GDT_CSRF.set_storage(tokens, user)
        return True
