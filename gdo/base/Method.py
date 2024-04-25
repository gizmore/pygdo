import argparse
from line_profiler_pycharm import profile
from gdo.base.Exceptions import GDOError
from gdo.base.GDT import GDT
from gdo.base.Trans import t, thas
from gdo.base.Util import Strings
from gdo.base.WithEnv import WithEnv
from gdo.base.WithError import WithError
from gdo.base.WithInput import WithInput


class WithPermissionCheck:
    def has_permission(self, user) -> bool:
        return True


class Method(WithEnv, WithInput, WithError, GDT):
    _parameters: dict[str, GDT]
    _server: object

    def __init__(self):
        super().__init__()
        self._params = {}
        self._next = None
        self._input = {}

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

    ############
    # Abstract #
    ############

    def gdo_parameters(self) -> [GDT]:
        return []

    def gdo_permission(self) -> str:
        return 'member'

    def gdo_execute(self):
        raise GDOError('err_stub')

    def gdo_render_title(self) -> str:
        return t(self._mome_tkey('mt'))

    def gdo_render_descr(self) -> str:
        return t(self._mome_tkey('md'))

    def gdo_render_usage(self) -> str:
        key = self._mome_tkey('mu')
        if thas(key):
            return t(key)
        return "unknown usage"#self._generate_usage()

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

    def _generate_usage(self) -> str:
        return self.get_arg_parser().format_usage()

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

    def param_val(self, key):
        for name, gdt in self.parameters().items():
            if key == name:
                value = gdt.to_value(gdt.get_val())
                if gdt.validate(value):
                    return gdt.get_val()
        return None

    def param_value(self, key):
        for name, gdt in self.parameters().items():
            if key == name:
                value = gdt.to_value(gdt.get_val())
                if gdt.validate(value):
                    return value
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
    def input(self, key, val):
        super().input(key, val)
        param = self.parameter(key)
        if param:
            param.val(val)
        return self

    def execute(self):
        """
        Check method environment and if allowed, gdo_execute() on permission
        """
        if not self.prepare():
            return self
        return self.gdo_execute()

    def prepare(self):
        if not self.has_permission(self._env_user):
            self.error('err_permission')
            return False
        return True

    def has_permission(self, user):
        return True

    def get_arg_parser(self, is_web: bool = True):
        parser = argparse.ArgumentParser(description=self.gdo_render_descr(), usage=self.gdo_render_usage())
        for gdt in self.parameters().values():
            if gdt.is_positional() and not is_web:
                parser.add_argument(gdt.get_name())
            else:
                parser.add_argument(f'--{gdt.get_name()}', default=gdt.get_initial())
        return parser


