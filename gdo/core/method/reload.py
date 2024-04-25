import importlib
import sys

from gdo.base.Method import Method
from gdo.base.Trans import Trans


class reload(Method):
    """
    Reload all gdo modules.
    """

    def cli_trigger(self) -> str:
        return 'reload'

    def gdo_execute(self):
        importlib.invalidate_caches()
        for module_name, module in list(sys.modules.items()):
            if module_name.startswith('gdo.') and not module_name.startswith('gdo.base'):
                try:
                    importlib.reload(module)
                except Exception as e:
                    self.err('err_reload_module', [module_name, str(e)])

        Trans.reload()
        return self.msg('msg_modules_reloaded')
