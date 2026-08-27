from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Render import Render
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDT_String import GDT_String


class server_set(Method):
    """Inspect or update one persisted Dog server setting."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'server.set'

    @classmethod
    def gdo_trig(cls) -> str:
        return 'srv.set'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return [
            # The server is an optional named selector.  Keeping it
            # non-positional lets `$server.set serv_trigger` address the
            # current server's setting instead of treating `serv_trigger` as
            # a server name.
            GDT_Server('server').not_null().default_current().positional(False),
            GDT_String('var_name').ascii().maxlen(64).positional(),
            GDT_RestOfText('new_var_value').positional(),
        ]

    def gdo_execute(self) -> GDT:
        server = self.param_value('server')
        name = self.param_val('var_name')
        value = self.param_val('new_var_value')
        mode = self._env_mode

        if not name:
            settings = ', '.join(
                f'{column.get_name()}={self.render_setting(column.gdo(server), mode)}'
                for column in server.columns().values()
            )
            return self.reply('msg_server_settings', (server.get_name(), settings))

        column = server.column(name)
        if column is None or name in ('serv_id', 'serv_created'):
            return self.err('err_server_set_unknown', (name,))
        column.gdo(server)
        if value is None:
            return self.reply('msg_server_setting', (
                server.get_name(), name, self.render_setting(column, mode),
            ))

        value = None if value == GDT.NULL_STRING else value
        old = self.render_setting(column, mode)
        if value == server.gdo_val(name):
            return self.reply('msg_server_setting_set', (server.get_name(), name, old, old))
        column.val(value)
        if not column.validated():
            return self.err('err_server_set_invalid', (name, column.render_error()))
        server.save_val(name, column.get_val())
        return self.reply('msg_server_setting_set', (
            server.get_name(), name, old,
            self.render_setting(server.column(name).gdo(server), mode),
        ))

    @staticmethod
    def render_setting(column: GDT, mode) -> str:
        if column.is_secret():
            return Render.italic('***', mode) if column.get_val() else Render.italic('none', mode)
        return Render.italic(column.render_val(), mode)
