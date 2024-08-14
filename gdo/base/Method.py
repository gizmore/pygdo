import argparse
import functools

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOError, GDOParamError
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Trans import t, thas
from gdo.base.Util import Strings, err, dump
from gdo.base.WithEnv import WithEnv
from gdo.base.WithError import WithError
from gdo.base.WithInput import WithInput
from gdo.base.WithPermissionCheck import WithPermissionCheck


class MyArgParser(argparse.ArgumentParser):

    def error(self, message):
        pass
        # err('%s', [message])


class Method(WithPermissionCheck, WithEnv, WithInput, WithError, GDT):
    _parameters: dict[str, GDT]
    _next_method: object  # Method chaining
    _result: str

    def __init__(self):
        super().__init__()
        self._params = {}
        self._next = None
        self._input = {}
        self._args = []
        self._env_mode = Application.get_mode()
        self._env_http = True
        self._env_channel = None
        self._env_server = None
        self._env_reply_to = None

    def get_name(self):
        return self.__class__.__name__

    def fqn(self):
        return self.__module__ + '.' + self.__class__.__qualname__

    def is_processed(self) -> bool:
        return hasattr(self, '_result')

    ############
    # Abstract #
    ############

    def gdo_trigger(self) -> str:
        """
        The CLI/Text trigger for non Web connectors. Return an empty string to disable all CLI connectors.
        """
        module = self.module()
        return f"{module.get_name()}.{self.get_name()}"

    def gdo_parameters(self) -> [GDT]:
        return []

    def gdo_method_config_bot(self) -> [GDT]:
        return []

    def gdo_method_config_server(self) -> [GDT]:
        return []

    def gdo_method_config_channel(self) -> [GDT]:
        return []

    def gdo_method_config_user(self) -> [GDT]:
        return []

    def gdo_user_type(self) -> str | None:
        """
        Comma separated list of applicable user types
        Use this to restrict to members or guests.
        """
        return 'ghost,member,guest'

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
        return a permission name here from GDO_Permission table to restrict
        """
        return None

    def gdo_has_permission(self, user):
        """
        Completely free and flexible permission check
        """
        return True

    def gdo_execute(self):
        raise GDOError('err_stub')

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

    ###########
    # Private #
    ###########

    def site_keywords(self):
        return t('keywords') if thas('keywords') else 'PyGDO,Website,HTTP Handler,WSGI'

    def _mome(self):
        return self.module().get_name() + "." + self.get_name()

    def _mome_tkey(self, key: str) -> str:
        return f'{key}_{self.module().get_name()}_{self.get_name()}'

    ##############
    # Parameters #
    ##############

    def parameters(self, reset: bool = False) -> dict[str, GDT]:
        if not hasattr(self, '_parameters') and not reset:
            self._parameters = {}
            for gdt in self.gdo_parameters():
                self._parameters[gdt.get_name()] = gdt
        return self._parameters

    def parameter(self, name: str):
        self.parameters()
        if name in self._parameters:
            return self._parameters[name]
        return None

    def param_val(self, key: str, throw: bool = True):
        for name, gdt in self.parameters().items():
            if key == name:
                val = gdt.get_val()
                value = gdt.to_value(val)
                if gdt.validate(val, value):
                    return gdt.get_val()
                elif throw:
                    raise GDOParamError('err_param', [name, gdt.render_error()])
        return None

    def param_value(self, key: str, throw: bool = True) -> any:
        for name, gdt in self.parameters().items():
            if key == name:
                val = gdt.get_val()
                value = gdt.to_value(val)
                if gdt.validate(val, value):
                    return value
                elif throw:
                    raise GDOParamError('err_param', [name, gdt.render_error()])
        return None

    # def init_params(self, params: dict):
    #     for key, val in params.items():
    #         self.parameter(key).val(val)
    #     return self

    ############
    # Redirect #
    ############
    def redirect(self, href: str):
        from gdo.ui.GDT_Page import GDT_Page
        from gdo.net.GDT_Redirect import GDT_Redirect
        redirect = GDT_Redirect().href(href)
        GDT_Page.instance()._top_bar.add_field(redirect)
        return self

    ###########
    # Message #
    ###########

    def empty(self, text: str = None) -> GDT:
        from gdo.ui.GDT_HTML import GDT_HTML
        html = GDT_HTML()
        if text:
            html.text('%s', [text])
        return html

    def reply(self, key: str, args: list = None):
        from gdo.core.GDT_String import GDT_String
        return GDT_String('reply').text(key, args)

    def msg(self, key: str, args: list = None):
        self.module().msg(key, args)
        return self

    def err(self, key: str, args: list = None):
        self.module().err(key, args)
        return self

    def module(self):
        from gdo.base.ModuleLoader import ModuleLoader
        mn = self.__module__
        mn = Strings.substr_from(mn, 'gdo.')
        mn = Strings.substr_to(mn, '.')
        return ModuleLoader.instance()._cache[mn]

    ########
    # Exec #
    ########
    def execute(self):
        """
        Check method environment and if allowed, gdo_execute() on permission
        """
        Application.set_current_user(self._env_user)
        if not self._prepare_nested_permissions(self):
            return self
        return self._nested_execute(self, True)

    def _nested_execute(self, method, return_gdt: bool = False):
        i = 0
        for arg in method._args:
            if isinstance(arg, Method):
                method._args[i] = self._nested_execute(arg)
                pass
            i += 1
        gdt = method._nested_execute_parse()
        if return_gdt:
            return gdt
        else:
            return gdt.render_txt()

    def _nested_parse(self):
        from gdo.core.GDT_Repeat import GDT_Repeat
        parser = self.get_arg_parser(False)
        args, unknown_args = parser.parse_known_args(self._args)
        for gdt in self.parameters().values():
            val = args.__dict__[gdt.get_name()] or ''
            if isinstance(val, list):
                gdt.val(val)
            else:
                # val = val.rstrip()
                if isinstance(gdt, GDT_Repeat):  # There may be one GDT_Repeat per method, which is the last param. append an array
                    vals = [val]
                    vals.extend(unknown_args)
                    gdt.val(vals)
                else:
                    gdt.val(val)

    def _nested_execute_parse(self):
        self._nested_parse()
        return self.gdo_execute()

    def _prepare_nested_permissions(self, method) -> bool:
        if not method.has_permission(method._env_user):
            self.error('err_permission')
            return False
        if not method.allows_connector():
            self.error('err_method_connector_not_supported')
            return False
        if method._env_channel and method._disabled_in_channel(method._env_channel):
            self.error('err_method_disabled')
        if method._disabled_in_server(method._env_server):
            self.error('err_method_disabled')

        for arg in method._args:
            if isinstance(arg, Method):
                if not self._prepare_nested_permissions(arg):
                    return False
        return True

    def _disabled_in_channel(self, channel):
        return False

    def _disabled_in_server(self, channel):
        return False

    def allows_connector(self) -> bool:
        connectors = self.gdo_connectors()
        if not connectors:
            return True
        connector = self._env_server.get_connector()
        return connector.get_name().lower() in connectors

    def get_arg_parser(self, for_usage: bool):
        return self._get_arg_parser_http(for_usage) if self._env_http else self._get_arg_parser_cli(for_usage)

    @functools.cache
    def _get_arg_parser_cli(self, for_usage: bool):
        from gdo.form.GDT_Submit import GDT_Submit
        prog = self.gdo_trigger()
        parser = MyArgParser(prog=prog, description=self.gdo_render_descr(), exit_on_error=True, add_help=False, allow_abbrev=False)
        for gdt in self.parameters().values():
            name = gdt.get_name()
            if for_usage and isinstance(gdt, GDT_Submit) and gdt._default_button:
                continue
            if gdt.is_positional():
                if gdt.is_not_null():
                    parser.add_argument(name)
                else:
                    parser.add_argument(name, nargs='?')
            else:
                parser.add_argument(f'--{name}', default=gdt.get_initial())
        self._parser = parser
        return parser

    @functools.cache
    def _get_arg_parser_http(self, for_usage: bool):
        prog = self.get_name()
        parser = MyArgParser(prog=prog, description=self.gdo_render_descr(), exit_on_error=True, add_help=False, allow_abbrev=False)
        for gdt in self.parameters().values():
            name = gdt.get_name()
            if gdt.is_multiple():
                parser.add_argument(f'--{name}', default=gdt.get_initial(), nargs='*')
            else:
                parser.add_argument(f'--{name}', default=gdt.get_initial())
        self._parser = parser
        return parser

    ##########
    # Config #
    ##########

    def get_fqn(self) -> str:
        return self.__module__ + "." + self.__class__.__name__

    #################
    # Config Server #
    #################

    def _config_server(self):
        from gdo.core.GDT_Bool import GDT_Bool
        conf = [
            GDT_Bool('disabled').initial('0'),
        ]
        conf.extend(self.gdo_method_config_server())
        return conf

    def save_config_server(self, key: str, val: str):
        Logger.debug(f"{self.get_name()}.save_config_server({key}, {val})")
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValServer import GDO_MethodValServer
        from gdo.core.GDO_MethodValServerBlob import GDO_MethodValServerBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_server():
            if gdt.get_name() == key:
                table = GDO_MethodValServerBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValServer.table()
                gdom = GDO_Method.for_method(self)
                entry = table.get_by_id(gdom.get_id(), self._env_server.get_id(), key)
                if entry is None:
                    table.blank({
                        'mv_method': gdom.get_id(),
                        'mv_server': self._env_server.get_id(),
                        'mv_key': key,
                        'mv_val': val,
                    }).insert()
                else:
                    entry.save_val('mv_val', val)

    def get_config_server(self, key: str) -> GDT:
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValServer import GDO_MethodValServer
        from gdo.core.GDO_MethodValServerBlob import GDO_MethodValServerBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_server():
            if gdt.get_name() == key:
                table = GDO_MethodValServerBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValServer.table()
                gdom = GDO_Method.for_method(self)
                entry = table.get_by_id(gdom.get_id(), self._env_server.get_id(), key)
                if entry:
                    gdt.initial(entry.get_val())
                return gdt

    def get_config_server_val(self, key: str) -> str:
        return self.get_config_server(key).get_val()

    def get_config_server_value(self, key: str):
        return self.get_config_server(key).get_value()

    ##################
    # Config Channel #
    ##################

    def _config_channel(self):
        from gdo.core.GDT_Bool import GDT_Bool
        conf = [
            GDT_Bool('disabled').initial('0'),
        ]
        conf.extend(self.gdo_method_config_channel())
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
        from gdo.core.GDO_Method import GDO_Method
        from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
        from gdo.core.GDO_MethodValChannelBlob import GDO_MethodValChannelBlob
        from gdo.core.GDT_Text import GDT_Text
        for gdt in self._config_channel():
            if gdt.get_name() == key:
                table = GDO_MethodValChannelBlob.table() if isinstance(gdt, GDT_Text) else GDO_MethodValChannel.table()
                if self._env_channel:
                    entry = table.get_by_id(GDO_Method.for_method(self).get_id(), self._env_channel.get_id(), None, None)
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
                parser = self.get_arg_parser(True)
                return parser.format_usage()
        return self.render_page().render(mode)

    def render_html(self) -> str:
        return self.render_page().render(Mode.HTML)

    def render_cli(self) -> str:
        return ''

    def render_txt(self) -> str:
        return ''

    ########
    # Temp #
    ########
    def temp_path_session(self, append: str = ''):
        mome = self._mome()
        sessid = self._env_session.get_id()
        return Application.temp_path(f"{mome}/{sessid}/{append}")
