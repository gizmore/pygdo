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

from gdo.user.GDT_ProfileLink import GDT_ProfileLink

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
        self._lax_server = False
        self._server_context = None
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

    def server_context(self, server) -> Self:
        self._server_context = server
        return self

    def scope_server(self, query: Query, val_serv: str | None) -> Query:
        if val_serv:
            from gdo.core.GDO_Server import GDO_Server
            if server := GDO_Server.table().get_by_vals({'serv_name': val_serv}):
                query.where(f'user_server={server.get_id()}')
            elif val_serv.isdecimal():
                query.where(f'user_server={val_serv}')
            else:
                query.where('1=0')
        if self._same_channel:
            query.where(f'user_server={self._same_channel.get_server().get_id()}')
        elif self._same_server:
            server_id = (self._server_context.get_id() if self._server_context
                         else GDO_User.current().get_server_id())
            query.where(f'user_server={server_id}' if server_id else '1=0')
        return query

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
        return self.scope_server(query, val_serv).limit(16)

    def query_gdos(self, val: str) -> list[GDO]:
        user_id = val if val.isnumeric() else Strings.regex_first(r'^(\d+)-', val)
        if user_id:
            val_serv = Strings.regex_first(r'{([^{}]+)}$', StringsUtil.utf8deobfuscate(val))
            query = self._table.select().where(f'user_id={int(user_id)}')
            users = self.scope_server(query, val_serv).limit(1).exec().fetch_all()
            if self._same_channel:
                users = [user for user in users if user.get_name() in self._same_channel._users]
            return users
        val_serv = Strings.regex_first(r'{([^{}]+)}$', StringsUtil.utf8deobfuscate(val))
        # With no explicit server, prefer an exact match on the request server.
        # Do not restrict other searches to that server: a remote-only user
        # must still be reachable, and lax mode treats exact duplicates equally.
        if not val_serv and not self._lax_server and not self._same_channel:
            server_id = (self._server_context.get_id() if self._server_context
                         else GDO_User.current().get_server_id())
            if server_id:
                local_query = self.query_gdos_query(val, self._table.select(), True)
                local = local_query.where(f'user_server={server_id}').limit(10).exec().fetch_all()
                if local:
                    return local
        # A complete nickname is never an invitation to expand into lookalikes.
        # Resolve it first; only fall back to completion-style matching if absent.
        exact = self.query_gdos_query(val, self._table.select(), True).limit(10).exec().fetch_all()
        if exact and self._same_channel:
            exact = [user for user in exact if user.get_name() in self._same_channel._users]
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
        self.scope_server(prefix_query, val_serv)
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

    def get_by_name(self, var: str | int):
        users = self.query_gdos(str(var).lower())
        if self._multiple:
            return users
        if len(users) == 1:
            return users[0]
        if len(users) > 1:
            self.error('err_select_candidates', ('|'.join(user.get_name_sid() for user in users),))
        return None

    ##########
    # Render #
    ##########

    def render_html(self) -> str:
        if user := self.get_gdo():
            return GDT_ProfileLink().user(user).with_avatar().render_html()
        return Render.italic(t('none'))

    def render_cell(self):
        return self.render_html()

    def html_cell_class(self) -> str:
        return 'shrink'
