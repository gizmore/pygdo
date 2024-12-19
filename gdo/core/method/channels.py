from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Server import GDT_Server


class channels(Method):

    def gdo_trigger(self) -> str:
        return 'channels'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Server('server').not_null().default_current(),
        ]

    def get_server(self) -> GDO_Server:
        return self.param_value('server')

    def gdo_execute(self) -> GDT:
        out = []
        serv = self.get_server()
        channels = serv.query_channels()
        for chan in channels:
            out.append(f"{chan.get_id()}-{chan.render_name()}")
        return self.reply('msg_channels', [len(channels), self._env_server.render_name(), ", ".join(out)])
