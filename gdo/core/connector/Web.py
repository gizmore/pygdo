from gdo.base.Render import Mode
from gdo.core.Connector import Connector
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_Server import GDO_Server


class Web(Connector):

    PUBLIC_NAME: str = 'public'
    PUBLIC: GDO_Channel = None

    def get_render_mode(self) -> Mode:
        return Mode.HTML

    @classmethod
    def get_server(cls) -> GDO_Server:
        return GDO_Server.get_by_connector('web')

    @classmethod
    def get_public_channel(cls) -> GDO_Channel:
        if not cls.PUBLIC:
            cls.PUBLIC = cls.get_server().get_or_create_channel(cls.PUBLIC_NAME)
        return cls.PUBLIC

    async def gdo_connect(self) -> bool:
        self._connected = True
        return True
