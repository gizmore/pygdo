from gdo.base.Application import Application
from gdo.core.GDT_Token import GDT_Token
from gdo.form.GDT_Hidden import GDT_Hidden


class GDT_CSRF(GDT_Hidden):
    TOKEN_LEN = 12

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
        sess = Application.get_session()
        tokens = sess.get('csrf', [])
        tokens.append(token)
        sess.set('csrf', tokens[-10:])
        return token

    def validate(self, value: any) -> bool:
        if Application.is_unit_test():
            return True
        sess = Application.get_session()
        tokens = sess.get('csrf', [])
        if value not in tokens:
            return self.error('err_csrf')
        tokens.remove(value)
        sess.set('csrf', tokens)
        return True

