import importlib
import sys

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import Trans


class reload(Method):
    """
    Reload all gdo modules.
    """

    def gdo_trigger(self) -> str:
        return 'reload'

    def gdo_user_permission(self) -> str | None:
        return "admin"

    def gdo_execute(self) -> GDT:
        importlib.invalidate_caches()
        for module_name, module in list(sys.modules.items()):
            if module_name.startswith('gdo.') and not module_name.startswith('gdo.base') and not module_name.startswith('gdo.core'):
                try:
                    importlib.reload(module)
                except Exception as e:
                    self.err('err_reload_module', (module_name, str(e)))

        Trans.reload()
        ModuleLoader.instance().reload_modules()
        return self.msg('msg_modules_reloaded')
