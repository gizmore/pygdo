import argparse

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOError, GDOParamError
from gdo.base.GDT import GDT
from gdo.base.Trans import t, thas
from gdo.base.Util import Strings, href, module_enabled, Arrays
from gdo.base.WithEnv import WithEnv
from gdo.base.WithError import WithError
from gdo.base.WithInput import WithInput


class Method(WithEnv, WithInput, WithError, GDT):
    _parameters: dict[str, GDT]
    _server: object
    _next_method: object  # Method chaining
    _result: str
    _parser: object

    def __init__(self):
        super().__init__()
        self._params = {}
        self._next = None
        self._input = {}
        self._args = []
        self._env_mode = Application.get_mode()
        self._env_http = True

    def server(self, server):
        self._server = server
        return self

    def cli_trigger(self) -> str:
        module = self.module()
        return f"{module.get_name()}.{self.get_name()}"

    def get_name(self):
        return self.__class__.__name__

    def fqn(self):
        return self.__module__ + '.' + self.__class__.__qualname__

    def is_processed(self) -> bool:
        return hasattr(self, '_result')

    ############
    # Abstract #
    ############

    def gdo_parameters(self) -> [GDT]:
        return []

    def gdo_user_type(self) -> str | None:
        """
        Comma separated list of applicable user types
        Use this to restrict to members or guests.
        """
        return 'member'

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

    # def gdo_render_usage(self) -> str:
    #     key = self._mome_tkey('mu')
    #     if thas(key):
    #         return t(key)
    #     return "unknown usage"#self._generate_usage()

    def gdo_render_keywords(self) -> str:
        kw = self.site_keywords()
        key = self._mome_tkey('mk')
        if thas(key):
            return f"{kw},{t(key)}"
        return kw

    def site_keywords(self):
        return t('keywords') if thas('keywords') else 'PyGDO,Website,HTTP Handler,WSGI'

    def _mome(self):
        return self.module().get_name() + "." + self.get_name()

    def _mome_tkey(self, key: str) -> str:
        return f'{key}_{self.module().get_name()}_{self.get_name()}'

    # def _generate_usage(self) -> str:
    #     return self.get_arg_parser().format_usage()

    ##############
    # Parameters #
    ##############

    def parameters(self) -> dict[str, GDT]:
        if not hasattr(self, '_parameters'):
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
                value = gdt.to_value(gdt.get_val())
                if gdt.validate(value):
                    return gdt.get_val()
                elif throw:
                    raise GDOParamError('err_param', [name, gdt.render_error()])
        return None

    def param_value(self, key: str, throw: bool = True):
        for name, gdt in self.parameters().items():
            if key == name:
                value = gdt.to_value(gdt.get_val())
                if gdt.validate(value):
                    return value
                elif throw:
                    raise GDOParamError('err_param', [name, gdt.render_error()])
        return None

    def init_params(self, params: dict):
        for key, val in params.items():
            self.parameter(key).val(val)
        return self

    ###########
    # Message #
    ###########

    def msg(self, key, args: list = None):
        return self.module().msg(key, args)

    def err(self, key, args: list = None):
        return self.module().err(key, args)

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
        if not self.prepare():
            return self
        return self._nested_execute(self, True)

    def prepare(self):
        return True

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

    def _nested_execute_parse(self):
        from gdo.core.GDT_Repeat import GDT_Repeat
        parser = self.get_arg_parser(self._env_http)
        args, unknown_args = parser.parse_known_args(self._args)
        for gdt in self.parameters().values():
            val = args.__dict__[gdt.get_name()] or ''
            val = val.rstrip()
            if isinstance(gdt, GDT_Repeat):  # There may be one GDT_Repeat per method, which is the last param. append an array
                vals = [val]
                vals.extend(unknown_args)
                gdt.val(vals)
            else:
                gdt.val(val)
        return self.gdo_execute()

    def _prepare_nested_permissions(self, method) -> bool:
        if not method.has_permission(method._env_user):
            self.error('err_permission')
            return False
        for arg in method._args:
            if isinstance(arg, Method):
                if not self._prepare_nested_permissions(arg):
                    return False
        return True

    def has_permission(self, user):
        return self.gdo_has_permission(user)

    def get_arg_parser(self, is_http: bool):
        if hasattr(self, '_parser'):
            return self._parser
        prog = self.get_name() if is_http else self.cli_trigger()
        parser = argparse.ArgumentParser(prog=prog, description=self.gdo_render_descr())
        for gdt in self.parameters().values():
            name = gdt.get_name()
            if gdt.is_positional() and not is_http:
                if gdt.is_not_null():
                    parser.add_argument(name)
                else:
                    parser.add_argument(name, nargs='?')
            else:
                parser.add_argument(f'--{name}', default=gdt.get_initial())
        self._parser = parser
        return parser
