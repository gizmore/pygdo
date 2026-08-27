from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Render import Render
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_String import GDT_String


class channel_set(Method):
    """Inspect or update one persisted channel setting."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'channel.set'

    @classmethod
    def gdo_trig(cls) -> str:
        return 'chan.set'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Channel('channel').not_null().default_current(),
            GDT_String('var_name').ascii().maxlen(64).positional(),
            GDT_RestOfText('new_var_value').positional(),
        ]

    def gdo_execute(self) -> GDT:
        channel = self.param_value('channel')
        name = self.param_val('var_name')
        value = self.param_val('new_var_value')
        mode = self._env_mode

        if not name:
            settings = ', '.join(
                f'{column.get_name()}={self.render_setting(column.gdo(channel), mode)}'
                for column in channel.columns().values()
            )
            return self.reply('msg_channel_settings', (channel.render_name(), settings))

        column = channel.column(name)
        if column is None or name in ('chan_id', 'chan_server', 'chan_created', 'chan_creator'):
            return self.err('err_channel_set_unknown', (name,))
        column.gdo(channel)
        if value is None:
            return self.reply('msg_channel_setting', (
                channel.render_name(), name, self.render_setting(column, mode),
            ))

        value = None if value == GDT.NULL_STRING else value
        old = self.render_setting(column, mode)
        if value == channel.gdo_val(name):
            return self.reply('msg_channel_setting_set', (channel.render_name(), name, old, old))
        column.val(value)
        if not column.validated():
            return self.err('err_channel_set_invalid', (name, column.render_error()))
        channel.save_val(name, column.get_val())
        return self.reply('msg_channel_setting_set', (
            channel.render_name(), name, old,
            self.render_setting(channel.column(name).gdo(channel), mode),
        ))

    @staticmethod
    def render_setting(column: GDT, mode) -> str:
        if column.is_secret():
            return Render.italic('***', mode) if column.get_val() else Render.italic('none', mode)
        return Render.italic(column.render_val(), mode)
