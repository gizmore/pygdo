from gdo.base.GDO import GDO
from typing_extensions import Self
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.Util import Strings, StringsUtil
from gdo.base.util.href import href
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Object import GDT_Object
from gdo.ui.GDT_Link import GDT_Link

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.core.GDO_Channel import GDO_Channel


class GDT_User(GDT_Object):
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
        self.with_completion()
        self.icon('user')

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

    def with_completion(self, with_completion: bool = True):
        if with_completion:
            self.completion(href('core', 'user_completion', '', 'json'))
        else:
            self.completion(None)
        return self

    def query_gdos_query(self, val: str, query: Query, exact: bool = False) -> Query:
        val = StringsUtil.utf8deobfuscate(val)
        val_serv = Strings.regex_first(r'{([^{}]+)}$', val)
        val = Strings.substr_to(val, '{', val)
        val = GDT.escape(val)
        if exact:
            query.where(f"(user_displayname='{val}' OR user_name='{val}')")
        else:
            query.where(f"(user_displayname LIKE '%{val}%' OR user_name LIKE '%{val}%')")
        if val_serv:
            from gdo.core.GDO_Server import GDO_Server
            if server := GDO_Server.table().get_by_vals({'serv_name': val_serv}):
                query.where(f"user_server={server.get_id()}")
            elif val_serv.isdecimal():
                query.where(f"user_server={val_serv}")
            else:
                query.where('1=0')
        if self._same_channel:
            query.where(f'user_server={self._same_channel.get_server().get_id()}')
        elif self._same_server:
            user = GDO_User.current()
            query.where(f'user_server={user.get_server_id()}')
        return query.limit(16)

    def query_gdos(self, val: str) -> list[GDO]:
        if val.isnumeric():
            if user := self._table.get_by_aid(val):
                return [user]
            return []
        if user_id := Strings.regex_first(r'^(\d+)-', val):
            if user := self._table.get_by_aid(user_id):
                return [user]
            return []
        # A complete nickname is never an invitation to expand into lookalikes.
        # Resolve it first; only fall back to completion-style matching if absent.
        exact = self.query_gdos_query(val, self._table.select(), True).limit(10).exec().fetch_all()
        if exact:
            return exact
        # Prefer an unambiguous nickname prefix over a broad substring match.
        # IRC users often enter just the first character of a distinctive nick;
        # expanding that into every account that merely contains the character is
        # surprising and prevents otherwise resolvable commands.
        prefix_query = self._table.select()
        prefix = Strings.substr_to(StringsUtil.utf8deobfuscate(val), '{', val)
        prefix = GDT.escape(prefix)
        prefix_query.where(f"(user_displayname LIKE '{prefix}%' OR user_name LIKE '{prefix}%')")
        val_serv = Strings.regex_first(r'{([^{}]+)}$', StringsUtil.utf8deobfuscate(val))
        if val_serv:
            from gdo.core.GDO_Server import GDO_Server
            if server := GDO_Server.table().get_by_vals({'serv_name': val_serv}):
                prefix_query.where(f"user_server={server.get_id()}")
            elif val_serv.isdecimal():
                prefix_query.where(f"user_server={val_serv}")
            else:
                prefix_query.where('1=0')
        if self._same_channel:
            prefix_query.where(f'user_server={self._same_channel.get_server().get_id()}')
        elif self._same_server:
            prefix_query.where(f'user_server={GDO_User.current().get_server_id()}')
        prefix_users = prefix_query.limit(2).exec().fetch_all()
        if self._same_channel:
            allowed_names = self._same_channel._users
            prefix_users = [user for user in prefix_users if user.get_name() in allowed_names]
        if len(prefix_users) == 1:
            return prefix_users
        query = self._table.select()
        users = self.query_gdos_query(val, query).limit(10).exec().fetch_all()
        if self._same_channel:
            allowed_names = self._same_channel._users
            return [user for user in users if user.get_name() in allowed_names]
        return users

    ##########
    # Render #
    ##########

    def render_html(self) -> str:
        if user := self.get_gdo():
            name = user.render_name()
            profile_id = f'{user.get_id()}-{user.get_name_sid()}'
            return GDT_Link().text_raw(name).href(href('user', 'profile', f'&for={profile_id}')).render()
        return Render.italic(t('none'))
