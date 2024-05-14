from typing_extensions import Self

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Util import Strings
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Object import GDT_Object
from gdo.core.WithCompletion import WithCompletion


class GDT_User(WithCompletion, GDT_Object):
    _same_server: bool
    _same_channel: bool
    _authenticated: bool
    _no_guests: bool

    def __init__(self, name):
        super().__init__(name)
        from gdo.core.GDO_User import GDO_User
        self.table(GDO_User.table())
        self._no_guests = False
        self._same_server = False
        self._same_channel = False
        self._authenticated = False

    def same_server(self, same_server: bool = True) -> Self:
        self._same_server = same_server
        return self

    def same_channel(self, same_channel: bool = True) -> Self:
        self._same_channel = same_channel
        return self

    def authenticated(self, authenticated: bool = True) -> Self:
        self._authenticated = authenticated
        return self

    def online(self, online: bool = True) -> Self:
        return self.authenticated(online)

    def query_gdos(self, val: str) -> list[GDO]:
        val_serv = Strings.regex_first(r'{(\d+)}$', val)
        val = Strings.substr_to(val, '{', val)
        query = self._table.select().where(f"user_id={GDT.quote(val)} OR user_displayname LIKE '%{GDT.escape(val)}%'")
        if val_serv:
            query.where(f"user_server={val_serv}")
        if self._same_server:
            user = GDO_User.current()
            query.where(f'user_server={user.get_server_id()}')
        return query.limit(10).exec().fetch_all()
