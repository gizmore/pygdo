from gdo.account.method.settings import settings
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Field import GDT_Field
from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Link import GDT_Link


class all_settings(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def has_visible_settings(self, module) -> bool:
        for gdt in module.all_user_settings():
            if isinstance(gdt, GDT_Link):
                return True
            if isinstance(gdt, GDT_Field) and gdt.is_writable():
                if not gdt.is_secret() or self._env_user.is_staff():
                    return True
        return False

    async def gdo_execute(self) -> GDT:
        cont = GDT_Container().vertical()
        loader = ModuleLoader.instance()
        methods = []
        for module in loader._cache.values():
            if self.has_visible_settings(module):
                method = settings().args_copy(self, True).env_copy(self).input('module', module.get_name)
                cont.add_field(method)
                methods.append(method)
        for method in methods:
            await method.execute()
        return cont
