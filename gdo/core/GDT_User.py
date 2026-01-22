from gdo.base.GDO import GDO
from typing_extensions import Self
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.Util import Strings
from gdo.base.util.href import href
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Object import GDT_Object
from gdo.core.WithCompletion import WithCompletion
from gdo.ui.GDT_Link import GDT_Link

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.core.GDO_Channel import GDO_Channel


class GDT_User(WithCompletion, GDT_Object):
    _same_server: bool
    _same_channel: 'GDO_Channel|None'
    _authenticated: bool
    _no_guests: bool
    _myself: bool

    def __init__(self, name):
        super().__init__(name)
        from gdo.core.GDO_User import GDO_User
        self.table(GDO_User.table())
        self._myself = False
        self._no_guests = False
        self._same_server = False
        self._same_channel = None
        self._authenticated = False

    def myself(self, myself: bool = True):
        self._myself = myself
        return self

    def same_server(self, same_server: bool = True) -> Self:
        self._same_server = same_server
        return self

    def same_channel(self, same_channel: 'GDO_Channel') -> Self:
        self._same_channel = same_channel
        if same_channel: self._same_server = True
        return self

    def authenticated(self, authenticated: bool = True) -> Self:
        self._authenticated = authenticated
        return self

    def online(self, online: bool = True) -> Self:
        return self.authenticated(online)

    def query_gdos_query(self, val: str, query: Query) -> Query:
        val_serv = Strings.regex_first(r'{(\d+)}$', val)
        val = Strings.substr_to(val, '{', val)
        query.where(f"user_displayname LIKE '%{GDT.escape(val)}%'")
        if val_serv:
            query.where(f"user_server={val_serv}")
        if self._same_server:
            user = GDO_User.current()
            query.where(f'user_server={user.get_server_id()}')
        return query.limit(10)

    def query_gdos(self, val: str) -> list[GDO]:
        if val.isnumeric():
            if user := self._table.get_by_aid(val):
                return [user]
            return []
        query = self._table.select()
        users = self.query_gdos_query(val, query).limit(10).exec().fetch_all()
        if self._same_channel:
            allowed = set(self._same_channel._users)
            return [user for user in users if user in allowed]
        return users

    ##########
    # Render #
    ##########

    def render_html(self) -> str:
        if user := self.get_gdo():
            name = user.render_name()
            return GDT_Link().text_raw(name).href(href('user', 'profile', f'&for={name}')).render()
        return Render.italic(t('none'))
