import functools
from asyncio import iscoroutine
from functools import lru_cache

from typing import TYPE_CHECKING, Self

from mysql.connector import OperationalError

from gdo.base.Cache import Cache
from gdo.base.ParseArgs import ParseArgs
from gdo.base.UserTemp import UserTemp
from gdo.message.GDT_HTML import GDT_HTML
from gdo.ui.GDT_Error import GDT_Error
from gdo.ui.GDT_Success import GDT_Success

if TYPE_CHECKING:
    from gdo.base.ParseArgs import ParseArgs
    from gdo.core.GDO_Channel import GDO_Channel
    from gdo.core.GDO_Server import GDO_Server
    from gdo.core.GDO_User import GDO_User
    from gdo.base.GDO_Module import GDO_Module

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOError, GDOParamError
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Trans import t, thas
from gdo.base.Util import err_raw
from gdo.base.WithEnv import WithEnv
from gdo.base.WithError import WithError
from gdo.base.WithPermissionCheck import WithPermissionCheck


class Method(WithPermissionCheck, WithEnv, WithError, GDT):
    _parameters: dict[str,GDT]
    _next_method: 'Method'  # Method chaining
    _result: str
    _raw_args: 'ParseArgs'
    _ppos: int
    _module: 'GDO_Module'

    __slots__ = (
        '_parameters',
        '_next_method',
        '_result',
        '_raw_args',
        '_ppos',
        '_module',
    )

    def __init__(self):
        super().__init__()
        self._raw_args = ParseArgs()
        self._env_mode = Application.get_mode()
        self._env_http = True
        self._env_channel = None
        self._env_server = None
        self._env_reply_to = None
        self._ppos = 0

    def module(self, module: 'GDO_Module') -> Self:
        self._module = module
        return self

    def get_name(self):
        return self.__class__.__name__

    def fqn(self):
        return f"{self.__module__}.{self.__class__.__qualname__}"

    def is_processed(self) -> bool:
        return hasattr(self, '_result')

    def input(self, key: str, val: str):
        self._raw_args.add_get_vars({key: [val]})
        return self

    def args_copy(self, method: 'Method'):
        self._raw_args.args.update(method._raw_args.args)
        return self

    def args(self, args: ParseArgs):
        self._raw_args = args
        return self

    def get_files(self, key: str) -> list[tuple[str, str, bytes]]:
        return self._raw_args.files[key]

    ############
    # Abstract #
    ############
    @classmethod
    def gdo_cached(cls) -> int:
        return 0

    @classmethod
    def gdo_trigger(cls) -> str:
        """
        The CLI/Text trigger for non Web connectors. Return an empty string to disable all CLI connectors.
        """
        module = cls.gdo_module()
        return f"{module.get_name}.{cls.__name__}"

    @classmethod
    def gdo_trig(cls) -> str:
        return cls.gdo_trigger()

    def gdo_method_hidden(self) -> bool:
        return False

    def gdo_transactional(self) -> bool:
        return Application.get_request_method() != 'GET'

    def gdo_parameters(self) -> list[GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_bot(cls) -> list[GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_server(cls) -> list[GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_channel(cls) -> list[GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_user(cls) -> list[GDT]:
        return GDO.EMPTY_LIST

    def gdo_user_type(self) -> str | None:
        """
        Comma separated list of applicable user types
        Use this to restrict to members or guests.
        """
        return None # 'ghost,member,guest,chappy'

    def gdo_connectors(self) -> str:
        """
        Comma separated list of supported connectors. An empty string means all
        :return:
        :rtype:
        """
        return ''

    def gdo_in_private(self) -> bool:
        """
        Indicate if a command works in private.
        :return:
        :rtype:
        """
        return True

    def gdo_in_channels(self) -> bool:
        """
        Indicate if a method works in channels. Only affects server connectors that support channels.
        :return:
        :rtype:
        """
        return True

    def gdo_user_permission(self) -> str | None:
        """
        return a permission name csv here from GDO_Permission table to restrict
        """
        return None

    def gdo_has_permission(self, user: 'GDO_User'):
        """
        Completely free and flexible permission check
        """
        return True

    def gdo_needs_authentication(self) -> bool:
        """
        Required for IRC functions when a user is member, but not authed.
        """
        return False

    def gdo_needs_level(self) -> int:
        return 0

    def gdo_execute(self) -> GDT:
        raise GDOError('err_stub')

    def gdo_before_execute(self):
        pass

    def gdo_after_execute(self):
        pass

    def gdo_render_title(self) -> str:
        return t(self._mome_tkey('mt'))

    def gdo_render_descr(self) -> str:
        return t(self._mome_tkey('md'))

    def gdo_render_keywords(self) -> str:
        kw = self.site_keywords()
        key = self._mome_tkey('mk')
        if thas(key):
            return f"{kw},{t(key)}"
        return kw

    def gdo_is_auto_testable(self) -> bool:
        return True

    ###########
    # Private #
    ###########

    def site_keywords(self):
        return t('keywords') if thas('keywords') else 'PyGDO,Website,HTTP Handler,WSGI'

    def _mome(self):
        return f"{self.gdo_module().get_name}.{self.get_name()}"

    @functools.cache
    def _mome_tkey(self, key: str) -> str:
        return f'{key}_{self.gdo_module().get_name}_{self.get_name()}'

    def get_method_id(self) -> str:
        from gdo.core.GDO_Method import GDO_Method
        return GDO_Method.for_method(self).get_id()

    ##############
    # Parameters #
    ##############

    def parameters(self, reset: bool = False) -> dict[str,GDT]:
        if not hasattr(self, '_parameters') or reset:
            self._ppos = 0
            self._parameters = {}
            for gdt in self.gdo_parameters():
                self.init_parameter(gdt)
        return self._parameters

    def init_parameter(self, gdt: GDT) -> GDT:
        val = None
        self._parameters[gdt.get_name()] = gdt
        if gdt.is_positional():
            self._ppos += 1
            gdt.position(self._ppos)
            if gdt._position <= len(self._raw_args.pargs):
                if gdt.is_multiple():
                    val = self._raw_args.pargs[gdt._position - 1:]
                    val = None if not val else val
                else:
                    val = [self._raw_args.pargs[gdt._position - 1]]
                    val = None if not val else val
        if val is None:
            val = self._raw_args.get_val(gdt.get_name(), gdt.get_val())
        val = val[0] if type(val) is list and not gdt.is_multiple() else val
        return gdt.val(val)

    def parameter(self, key: str, init: bool = False) -> GDT:
        return self.parameters().get(key)

    def param_val(self, key: str, throw: bool = True) -> str|None:
        gdt = self.parameter(key)
        val = gdt.get_val()
        if gdt.validate(val):
            return val
        elif throw:
            raise GDOParamError('err_param', (key, gdt.render_error()))
        return None

    def param_value(self, key: str, throw: bool = True) -> any:
        gdt = self.parameter(key)
        if gdt.validate(gdt.get_val()):
            return gdt.get_value()
        elif throw:
            raise GDOParamError('err_param', (key, gdt.render_error()))
        return None

    def param_vals(self):
        vals = {}
        for _gdt in self.parameters().values():
            for gdt in _gdt.gdo_components():
                if name := gdt.get_name():
                    vals[name] = self.param_val(name)
        return vals

    ############
    # Redirect #
    ############
    def redirect(self, href: str, key: str = None, args: tuple[str|int|float,...] = None):
        from gdo.net.GDT_Redirect import GDT_Redirect
        redirect = GDT_Redirect().href(href)
        if key: redirect.text(key, args)
        Application.get_page()._top_bar.add_field(redirect)
        return self

    def redirect_msg(self, href: str, key: str, args: tuple[str | float | int, ...] = None):
        UserTemp.flash(self._env_user, GDT_Success().text(key, args).title_raw(self.gdo_module().render_name()))
        return self.redirect(href, key, args)

    def redirect_err(self, href: str, key: str, args: tuple[str | float | int, ...] = None):
        UserTemp.flash(self._env_user, GDT_Error().text(key, args).title_raw(self.gdo_module().render_name()))
        return self.redirect(href, key, args)

    def href(self, append: str = '', format: str = 'html') -> str:
        return self.gdo_module().href(self.get_name(), append, format)

    def execute_command(self, line: str):
        from gdo.base.Parser import Parser
        parser = Parser(self._env_mode, self._env_user, self._env_server, self._env_channel, self._env_session)
        method = parser.parse_line(line)
        return method.execute()

    ###########
    # Message #
    ###########

    def empty(self, text: str = None) -> GDT:
        from gdo.message.GDT_HTML import GDT_HTML
        html = GDT_HTML()
        if text:
            html.text(text)
        return html

    def reply(self, key: str, args: tuple = None):
        return  self.gdt_string()('reply').text(key, args)

    def msg(self, key: str, args: tuple = None):
        self.gdo_module().msg(key, args)
        return self

    def err(self, key: str, args: tuple = None):
        self.gdo_module().err(key, args)
        return self

    ########
    # Exec #
    ########
    METHOD_CACHE: dict[str, tuple[float, GDT]] = {}

    async def execute(self):
        if self.gdo_cached():
            key = self._raw_args.get_cache_key(self)
            if Cache.get_timed_cache(key):
                return GDT_HTML()
        db = Application.db()
        tr = self.gdo_transactional() and not db.is_in_transaction()
        try:
            if tr:
                db.begin()
            self.gdo_before_execute()
            if not self._prepare_nested_permissions(self):
                return self.empty()
            result = await self._nested_execute(self, True)
        except (GDOParamError, GDOError) as ex:
            err_raw(str(ex))
            return self
        except OperationalError as ex:
            db.reconnect()
            raise ex
        except Exception as ex:
            if tr:
                db.rollback()
                tr = False
            raise ex
        finally:
            if tr:
                db.commit()
        self.gdo_after_execute()
        return result

    async def _nested_execute(self, method: 'Method', return_gdt: bool = False):
        i = 0
        if method._raw_args:
            for key, arg in method._raw_args.all_vals():
                if isinstance(arg, Method):
                    cont = method._raw_args.pargs if type(key) is int else method._raw_args.args
                    cont[key] = await self._nested_execute(arg)
                i += 1
        gdt = await method._nested_execute_parse()
        while iscoroutine(gdt):
            gdt = await gdt
        if return_gdt:
            return gdt
        else:
            return gdt.render(Mode.render_txt)

    async def _nested_execute_parse(self) -> 'GDT':
        result = self.gdo_execute()
        self.gdo_after_execute()
        return result

    def _prepare_nested_permissions(self, method: 'Method') -> bool:
        if not self._env_user.is_authenticated():
            if token := self._raw_args.get_val('_auth'):
                if uid := self.validate_auth_token(token[0]):
                    from gdo.core.GDO_User import GDO_User
                    user = GDO_User.table().get_by_aid(uid)
                    self.env_user(user, False)
                    user._authenticated = True
                    Application.set_current_user(user)
                    return True
        if not method.has_permission(method._env_user):
            self.error('err_permissions')
            return False
        if method._raw_args:
            for key, arg in method._raw_args.all_vals():
                if isinstance(arg, Method):
                    if not self._prepare_nested_permissions(arg):
                        return False
        return True

    ##########
    # Config #
    ##########

    @functools.cache
    def get_sqn(self) -> str:
        return f"{self.gdo_module().get_name}.{self.get_name()}"

    @functools.cache
    def get_fqn(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}"

    @classmethod
    def gdo_default_enabled_server(cls) -> bool:
        return True

    @classmethod
    def gdo_default_enabled_channel(cls) -> bool:
        return True

    #################
    # Config Server #
    #################

    @classmethod
    @functools.lru_cache(None)
    def _config_server(cls):
        from gdo.core.GDT_Bool import GDT_Bool
        conf = [
            GDT_Bool('disabled').initial('0' if cls.gdo_default_enabled_server() else '1'),
        ]
        conf.extend(cls.gdo_method_config_server())
        return conf

    def save_config_server(self, key: str, val: str):
        return self._save_config_server(key, val, self._env_server)

    def _save_config_server(self, key: str, val: str, server: 'GDO_Server', known_fresh: bool = False):
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValServer import GDO_MethodValServer
        from gdo.core.GDO_MethodValServerBlob import GDO_MethodValServerBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_server():
            if gdt.get_name() == key:
                table = GDO_MethodValServerBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValServer.table()
                gdom = GDO_Method.for_method(self)
                entry = None if known_fresh else table.get_by_id(gdom.get_id(), server.get_id(), key)
                if entry is None:
                    table.blank({
                        'mv_method': gdom.get_id(),
                        'mv_server': server.get_id(),
                        'mv_key': key,
                        'mv_val': gdt.val(val).get_val(),
                    }).insert()
                else:
                    entry.save_val('mv_val', gdt.val(val).get_val())

    def get_config_server(self, key: str) -> GDT:
        return self._get_config_server(key, self._env_server)

    def _get_config_server(self, key: str, server: 'GDO_Server') -> GDT:
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValServer import GDO_MethodValServer
        from gdo.core.GDO_MethodValServerBlob import GDO_MethodValServerBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_server():
            if gdt.get_name() == key:
                table = GDO_MethodValServerBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValServer.table()
                gdom = GDO_Method.for_method(self)
                entry = table.get_by_id(gdom.get_id(), server.get_id(), key)
                if entry:
                    gdt.initial(entry.gdo_val('mv_val'))
                else:
                    self._save_config_server(key, gdt._initial, server, True)
                return gdt


    def get_config_server_val(self, key: str) -> str:
        return self.get_config_server(key).get_val()

    def get_config_server_value(self, key: str):
        return self.get_config_server(key).get_value()

    ###############
    # Config User #
    ###############

    @lru_cache
    def _config_user(self):
        return self.gdo_method_config_user()

    def save_config_user(self, key: str, val: str):
        Logger.debug(f"{self.get_name()}.save_config_user({key}, {val})")
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValUser import GDO_MethodValUser
        from gdo.core.GDO_MethodValUserBlob import GDO_MethodValUserBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_user():
            if gdt.get_name() == key:
                table = GDO_MethodValUserBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValUser.table()
                gdom = GDO_Method.for_method(self)
                entry = table.get_by_id(gdom.get_id(), self._env_user.get_id(), key)
                if entry is None:
                    table.blank({
                        'mv_method': gdom.get_id(),
                        'mv_user': self._env_user.get_id(),
                        'mv_key': key,
                        'mv_val': val,
                    }).insert()
                else:
                    entry.save_val('mv_val', val)

    def get_config_user(self, key: str) -> GDT:
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValUser import GDO_MethodValUser
        from gdo.core.GDO_MethodValUserBlob import GDO_MethodValUserBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_user():
            if gdt.get_name() == key:
                table = GDO_MethodValUserBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValUser.table()
                entry = table.get_by_id(GDO_Method.for_method(self).get_id(), self._env_user.get_id(), key)
                if entry:
                    gdt.initial(entry.get_val())
                return gdt

    def get_config_user_val(self, key: str) -> str:
        return self.get_config_user(key).get_val()

    def get_config_user_value(self, key: str):
        return self.get_config_user(key).get_value()

    ##################
    # Config Channel #
    ##################

    @classmethod
    @functools.lru_cache(None)
    def _config_channel(cls):
        from gdo.core.GDT_Bool import GDT_Bool
        conf = [
            GDT_Bool('disabled').initial('0' if cls.gdo_default_enabled_channel() else '1'),
        ]
        conf.extend(cls.gdo_method_config_channel())
        return conf

    def save_config_channel(self, key: str, val: str):
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
        from gdo.core.GDO_MethodValChannelBlob import GDO_MethodValChannelBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_channel():
            if gdt.get_name() == key:
                table = GDO_MethodValChannelBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValChannel.table()
                gdom = GDO_Method.for_method(self)
                entry = table.get_by_id(gdom.get_id(), self._env_channel.get_id(), key)
                if entry is None:
                    table.blank({
                        'mv_method': gdom.get_id(),
                        'mv_channel': self._env_channel.get_id(),
                        'mv_key': key,
                        'mv_val': val,
                    }).insert()
                else:
                    entry.save_val('mv_val', val)

    def get_config_channel(self, key: str) -> GDT:
        return self._get_config_channel(key, self._env_channel)

    def _get_config_channel(self, key: str, channel: 'GDO_Channel') -> GDT:
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
        from gdo.core.GDO_MethodValChannelBlob import GDO_MethodValChannelBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_channel():
            if gdt.get_name() == key:
                if channel:
                    table = GDO_MethodValChannelBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValChannel.table()
                    entry = table.get_by_id(GDO_Method.for_method(self).get_id(), channel.get_id(), key)
                    if entry:
                        gdt.initial(entry.get_val())
                return gdt

    def get_config_channel_val(self, key: str) -> str:
        return self.get_config_channel(key).get_val()

    def get_config_channel_value(self, key: str):
        return self.get_config_channel(key).get_value()

    def channels_with_setting(self, key: str, val: str, server: 'GDO_Server' = None):
        from gdo.core.GDO_Channel import GDO_Channel
        return GDO_Channel.with_setting(self, key, val, self.get_config_channel(key).get_initial(), server)

    ###

    def render_cli_usage(self) -> str:
        from gdo.core.GDT_Field import GDT_Field
        from gdo.form.GDT_Submit import GDT_Submit
        optional = []
        positional = []
        for gdt in self.parameters().values():
            if not isinstance(gdt, GDT_Field):
                continue
            if isinstance(gdt, GDT_Submit) and gdt._default_button:
                continue
            label = gdt.get_name()
            if not gdt.is_positional():
                optional.append(f"[--{label}=]")
            else:
                if gdt.is_not_null():
                    positional.append(f"<{label}>")
                else:
                    positional.append(f"[<{label}>]")
        return f"Usage: {self.gdo_trigger()} {' '.join(optional + positional)}"

    ##########
    # Render #
    ##########
    def render_page(self) -> GDT:
        return self.empty()

    def render(self, mode: Mode = Mode.render_html):
        if self.has_error():
            if self._env_http:
                from gdo.ui.GDT_Error import GDT_Error
                return GDT_Error().text(self._errkey, self._errargs).render_html()
            else:
                return self.render_cli_usage()
        return self.render_page().render(mode)

    def render_gdo(self, gdo: GDO, mode: Mode) -> str:
        return ''

    def render_html(self) -> str:
        return self.render_page().render(Mode.render_html)

    def render_cli(self) -> str:
        return ''

    def render_txt(self) -> str:
        return ''
