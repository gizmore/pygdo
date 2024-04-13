from gdo.base.Exceptions import GDOError
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t, thas
from gdo.base.Util import Strings
from gdo.base.WithEnv import WithEnv
from gdo.base.WithInput import WithInput
from gdo.core.GDT_String import GDT_String


class WithPermissionCheck:
    def has_permission(self, user) -> bool:
        return True


class Method(WithEnv, WithInput, GDT):
    _parameters: dict[str, GDT]

    def __init__(self):
        super().__init__()
        self._params = {}
        self._next = None

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
        return t(f'mt_{self._mome()}')

    def gdo_render_descr(self) -> str:
        return t(f'md_{self._mome()}')

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

        return self._parameters.__dict__

    def parameter(self, name: str):
        self.parameters()
        return self._parameters[name]

    def param_val(self, key):
        return

    def param_value(self, key):
        for name, gdt in self.parameters():
            if key == name:
                value = gdt.to_value(gdt.get_val())
                return gdt.validated(value)
        return None

    def message_raw(self, message):
        return self.message('%s', [message])

    def message(self, key, args):
        from gdo.ui.GDT_Success import GDT_Success
        return GDT_Success().title_raw(self.module().render_name())

    def error_raw(self, error):
        return self.error('%s', [error])

    def error(self, key, args):
        from gdo.ui.GDT_Error import GDT_Error
        return GDT_Error().title_raw(self.module().render_name()).add_field(GDT_String('error').initial())

    def module(self):
        mn = Strings.substr_from(self.__module__, 'gdo.')
        mn = Strings.substr_to(mn, '.')
        return ModuleLoader.instance()._cache[mn]

    def execute(self):
        """
        Check method environment and if allowed, gdo_execute() on permission
        :return:
        :rtype:
        """
        if not self.has_permission(self._user):
            return False

        return self.gdo_execute()

    def has_permission(self, user):
        pass

