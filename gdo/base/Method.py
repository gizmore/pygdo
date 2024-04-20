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

    def __init__(self):
        super().__init__()
        self._params = {}
        self._next = None

    def cli_trigger(self) -> str:
        module = self.module()
        return f"{module.get_name()}.{self.get_name()}"

    def get_name(self):
        return self.__class__.__name__

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
        return t(f'mt_{self._mome().replace(".", "_")}')

    def gdo_render_descr(self) -> str:
        return t(f'md_{self._mome().replace(".", "_")}')

    def gdo_render_usage(self) -> str:
        key = t(f'mu_{self._mome()}')
        if thas(key):
            return t(key)
        return self._generate_usage()

    def _generate_usage(self):
        return "USAGE_GEN"

    def gdo_render_keywd(self) -> str:
        return t(f'mk_{self._mome()}')

    def _mome(self):
        return self.module().get_name() + "." + self.get_name()

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

