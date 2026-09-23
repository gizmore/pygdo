from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User


class about(Method):
    """Show an about-me setting for the caller or one selected user."""

    MAX_CHAT_LENGTH = 360

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'about'

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_User('user').positional()]

    @classmethod
    def format_about(cls, text: str) -> str:
        """Keep a profile blurb to one safe, IRC-sized display line."""
        return ' '.join((text or '').split())[:cls.MAX_CHAT_LENGTH].rstrip()

    def get_user(self) -> GDO_User:
        return self.param_value('user') or self._env_user

    def gdo_execute(self) -> GDT:
        user = self.get_user()
        text = self.format_about(user.get_setting_val('about_me'))
        if not text:
            return self.reply('msg_user_about_empty', (user.render_name(),))
        return self.reply('msg_user_about', (user.render_name(), text))
