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

    @classmethod
    def gdo_trigger(cls) -> str:
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
        loader = ModuleLoader.instance()
        loader.reload_modules()
        # Newly added method files are hidden behind each module's cached
        # discovery result.  `$reload` is explicitly the hot-reload path, so
        # rebuild that list and the trigger maps from scratch.
        for module in loader._cache.values():
            module.get_method_klasses.cache_clear()
        loader._methods.clear()
        loader._meths.clear()
        # A module installed while this process was running has its instance
        # in the loader cache, but its command classes still need registering.
        # Keep `$reload` useful as the no-restart activation path.
        loader.init_cli()
        return self.msg('msg_modules_reloaded')
