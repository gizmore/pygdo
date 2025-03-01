import functools

from typing import TYPE_CHECKING

from mysql.connector import OperationalError

from gdo.base.ParseArgs import ParseArgs

if TYPE_CHECKING:
    from gdo.base.GDO_Module import GDO_Module
    from gdo.base.ParseArgs import ParseArgs
    from gdo.core.GDO_Channel import GDO_Channel
    from gdo.core.GDO_Server import GDO_Server
    from gdo.core.GDO_User import GDO_User

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOError, GDOParamError
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Trans import t, thas
from gdo.base.Util import Strings, err_raw
from gdo.base.WithEnv import WithEnv
from gdo.base.WithError import WithError
from gdo.base.WithPermissionCheck import WithPermissionCheck


class Method(WithPermissionCheck, WithEnv, WithError, GDT):
    _parameters: dict[str,GDT]
    _next_method: 'Method'  # Method chaining
    _result: str
    _raw_args: 'ParseArgs'

    __slots__ = (
        '_parameters',
        '_next_method',
        '_result',
        '_raw_args'
    )

    # CLI_PARSER_CACHE = {}
    # HTM_PARSER_CACHE = {}
    # _parser_http: argparse
    # _parser_clix: argparse
    # _parser_cliu: argparse

    def __init__(self):
        super().__init__()
        # self._params = {}
        # self._next = None
        # self._input = {}
        # self._args = []
        self._raw_args = ParseArgs()
        # self._raw_args = None
        self._env_mode = Application.get_mode()
        self._env_http = True
        self._env_channel = None
        self._env_server = None
        self._env_reply_to = None
        # self._parser_http = None
        # self._parser_clix = None
        # self._parser_cliu = None


    def get_name(self):
        return self.__class__.__name__

    @functools.cache
    def fqn(self):
        return self.__module__ + '.' + self.__class__.__qualname__

    def is_processed(self) -> bool:
        return hasattr(self, '_result')

    def input(self, key: str, val: str):
        self._raw_args.add_get_vars({key: val})
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

    def gdo_trigger(self) -> str:
        """
        The CLI/Text trigger for non Web connectors. Return an empty string to disable all CLI connectors.
        """
        module = self.gdo_module()
        return f"{module.get_name()}.{self.get_name()}"

    def gdo_transactional(self) -> bool:
        return Application.get_request_method() != 'GET'

    def gdo_parameters(self) -> [GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_bot(cls) -> [GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_server(cls) -> [GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_channel(cls) -> [GDT]:
        return GDO.EMPTY_LIST

    @classmethod
    def gdo_method_config_user(cls) -> [GDT]:
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
        return True

    def gdo_execute(self) -> GDT:
        raise GDOError('err_stub')

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
        return self.gdo_module().get_name() + "." + self.get_name()

    def _mome_tkey(self, key: str) -> str:
        return f'{key}_{self.gdo_module().get_name()}_{self.get_name()}'

    ##############
    # Parameters #
    ##############

    def parameters(self, reset: bool = False) -> dict[str, GDT]:
        if not hasattr(self, '_parameters') or reset:
            self._parameters = {gdt.get_name(): gdt for gdt in self.gdo_parameters()}
            self.set_parameter_positions()
        return self._parameters

    def set_parameter_positions(self):
        n = 1
        for gdt in self._parameters.values():
            if gdt.is_positional():
                gdt.position(n)
                n += 1

    def parameter(self, key: str) -> GDT:
        gdt = self.parameters().get(key)
        val = None
        if gdt.is_positional():
            if gdt._position <= len(self._raw_args.pargs):
                if gdt.is_multiple():
                    val = self._raw_args.pargs[gdt._position - 1:]
                else:
                    val = [self._raw_args.pargs[gdt._position - 1]]
        if val is None:
            val = self._raw_args.get_val(gdt.get_name(), gdt.get_val())
        val = val[0] if type(val) is list and not gdt.is_multiple() else val
        return gdt.val(val)

    def param_val(self, key: str, throw: bool = True) -> str|None:
        gdt = self.parameter(key)
        if gdt.validate(gdt.get_val(), gdt.get_value()):  # TODO: validate only by val, let validators cast lazily.
            return gdt.get_val()
        elif throw:
            raise GDOParamError('err_param', (key, gdt.render_error()))

    def param_value(self, key: str, throw: bool = True) -> any:
        gdt = self.parameter(key)
        if gdt.validate(gdt.get_val(), gdt.get_value()):  # TODO: validate only by val
            return gdt.get_value()
        elif throw:
            raise GDOParamError('err_param', (key, gdt.render_error()))

    ############
    # Redirect #
    ############
    def redirect(self, href: str):
        from gdo.net.GDT_Redirect import GDT_Redirect
        redirect = GDT_Redirect().href(href)
        Application.get_page()._top_bar.add_field(redirect)
        return self

    def href(self, append: str = '', format: str = 'html') -> str:
        return self.gdo_module().href(self.get_name(), append, format)

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
        from gdo.core.GDT_String import GDT_String
        return GDT_String('reply').text(key, args)

    def msg(self, key: str, args: tuple = None):
        self.gdo_module().msg(key, args)
        return self

    def err(self, key: str, args: tuple = None):
        self.gdo_module().err(key, args)
        return self

    @functools.cache
    def gdo_module(self) -> 'GDO_Module':
        from gdo.base.ModuleLoader import ModuleLoader
        mn = self.__module__
        mn = Strings.substr_from(mn, 'gdo.')
        mn = Strings.substr_to(mn, '.')
        return ModuleLoader.instance()._cache[mn]

    ########
    # Exec #
    ########
    async def execute(self):
        db = Application.db()
        tr = self.gdo_transactional() and not db.is_in_transaction()
        try:
            if tr:
                db.begin()
            if not self._prepare_nested_permissions(self):
                return self
            return await self._nested_execute(self, True)
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

    async def _nested_execute(self, method: 'Method', return_gdt: bool = False):
        # i = 0
        # if method._raw_args:
        #     for key, arg in method._raw_args.all_vals():
        #         if isinstance(arg, Method):
        #             cont = method._raw_args.pargs if type(key) is int else method._raw_args.args
        #             cont[key] = await self._nested_execute(arg)
        #         i += 1
        gdt = await method._nested_execute_parse()
        if return_gdt:
            return gdt
        else:
            return gdt.render(Mode.TXT)

    def _nested_parse(self):
        pass
        # if self._raw_args:
        #     for gdt in self.parameters().values():
        #         if val := self._raw_args.get_val(gdt.get_name()):
        #             if not gdt.is_multiple():
        #                 val = val[0]
        #             gdt.val(val)
#        from gdo.core.GDT_Repeat import GDT_Repeat
#        from gdo.core.GDT_Field import GDT_Field
        # parser = self.get_arg_parser(False)
        # args, unknown_args = parser.parse_known_args(self._args)
        # for gdt in self.parameters():
        #     if not isinstance(gdt, GDT_Field):
        #         continue
        #     if val := args.__dict__.get(gdt.get_name()):
        #         if isinstance(val, list):
        #             gdt.val(val)
        #         else:
        #             if isinstance(gdt, GDT_Repeat):  # There may be one GDT_Repeat per method, which is the last param. append an array
        #                 vals = [val]
        #                 vals.extend(unknown_args)
        #                 gdt.val(vals)
        #             else:
        #                 gdt.val(val)

    async def _nested_execute_parse(self) -> 'GDT':
        self._nested_parse()
        result = self.gdo_execute()
        self.gdo_after_execute()
        return result

    def _prepare_nested_permissions(self, method: 'Method') -> bool:
        if not method.has_permission(method._env_user):
            self.error('err_permissions')
            return False
        if method._raw_args:
            for key, arg in method._raw_args.all_vals():
                if isinstance(arg, Method):
                    if not self._prepare_nested_permissions(arg):
                        return False
        return True

    # def get_arg_parser(self, for_usage: bool):
    #     return self._get_arg_parser_http() if self._env_http else self._get_arg_parser_cli(for_usage)
    #
    # def _get_arg_parser_cli(self, for_usage: bool):
    #     if for_usage:
    #         if self._parser_cliu:
    #             return self._parser_cliu
    #     else:
    #         if self._parser_clix:
    #             return self._parser_clix
    #
    #     from gdo.form.GDT_Submit import GDT_Submit
    #     from gdo.core.GDT_Field import GDT_Field
    #     prog = self.gdo_trigger()
    #     parser = MyArgParser(prog=prog, description=self.gdo_render_descr(), exit_on_error=True, add_help=False, allow_abbrev=False)
    #     for gdt in self.parameters():
    #         if not isinstance(gdt, GDT_Field):
    #             continue
    #         name = gdt.get_name()
    #         if for_usage and isinstance(gdt, GDT_Submit) and gdt._default_button:
    #             continue
    #         if gdt.is_positional():
    #             if gdt.is_not_null():
    #                 parser.add_argument(name)
    #             else:
    #                 parser.add_argument(name, nargs='?')
    #         else:
    #             parser.add_argument(f'--{name}', default=gdt.get_val())
    #     if for_usage:
    #         self._parser_cliu = parser
    #     else:
    #         self._parser_clix = parser
    #     return parser
    #
    # def _get_arg_parser_http(self):
    #     if self._parser_http:
    #         return self._parser_http
    #     # fqn = self.fqn()
    #     # if fqn in self.HTM_PARSER_CACHE:
    #     #     Cache.HITS += 1 #PYPP#DELETE#
    #     #     return self.HTM_PARSER_CACHE[fqn]
    #     from gdo.core.GDT_Field import GDT_Field
    #     prog = self.get_name()
    #     parser = MyArgParser(prog=prog, description=self.gdo_render_descr(), exit_on_error=True, add_help=False, allow_abbrev=False)
    #     for gdt in self.parameters():
    #         if not isinstance(gdt, GDT_Field):
    #             continue
    #         name = gdt.get_name()
    #         if gdt.is_multiple():
    #             parser.add_argument(f'--{name}', default=gdt.get_val(), nargs='*')
    #         else:
    #             parser.add_argument(f'--{name}', default=gdt.get_val())
    #     # self.HTM_PARSER_CACHE[fqn] = parser
    #     self._parser_http = parser
    #     return parser

    ##########
    # Config #
    ##########

    @functools.cache
    def get_sqn(self) -> str:
        return f"{self.gdo_module().get_name()}.{self.get_name()}"

    @functools.cache
    def get_fqn(self) -> str:
        return self.__module__ + "." + self.__class__.__name__

    @classmethod
    def gdo_default_enabled(cls) -> bool:
        return True

    #################
    # Config Server #
    #################

    @classmethod
    @functools.lru_cache(None)
    def _config_server(cls):
        from gdo.core.GDT_Bool import GDT_Bool
        conf = [
            GDT_Bool('disabled').initial('0' if cls.gdo_default_enabled() else '1'),
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

    def _config_user(self):
        return GDO.EMPTY_LIST
        # from gdo.core.GDT_Bool import GDT_Bool
        # conf = [
        #     GDT_Bool('disabled').initial('0' if self.gdo_default_enabled() else '1'),
        # ]
        # conf.extend(self.gdo_method_config_user())
        # return conf

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
            GDT_Bool('disabled').initial('0' if cls.gdo_default_enabled() else '1'),
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

    def channels_with_setting(self, key: str, val: str):
        from gdo.core.GDO_Channel import GDO_Channel
        return GDO_Channel.with_setting(self._env_server, key, val, self.get_config_channel(key).get_initial())

    ###

    def render_cli_usage(self) -> str:
        positional = []
        optional = []
        for gdt in self.parameters().values():
            label = gdt.get_name()
            if not gdt.is_positional():
                optional.append(f"[--{label}]")
            else:
                positional.append(f"<{label}>")
        return f"{self.gdo_trigger()} {self.gdo_}\nUsage: {self.gdo_trigger()} {' '.join(optional + positional)}"

    ##########
    # Render #
    ##########
    def render_page(self) -> GDT:
        return self.empty()

    def render(self, mode: Mode = Mode.HTML):
        if self.has_error():
            if self._env_http:
                from gdo.ui.GDT_Error import GDT_Error
                return GDT_Error().text(self._errkey, self._errargs).render_html()
            else:
                return self.render_cli_usage()
                # parser = self.get_arg_parser(True)
                # return parser.format_usage()
        return self.render_page().render(mode)

    def render_gdo(self, gdo: GDO, mode: Mode) -> str:
        return ''

    def render_html(self) -> str:
        return self.render_page().render(Mode.HTML)

    def render_cli(self) -> str:
        return ''

    def render_txt(self) -> str:
        return ''
