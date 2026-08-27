from gdo.account.method.settings import settings
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Container import GDT_Container
from gdo.ui.GDT_Bar import GDT_Bar


class all_settings(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    async def gdo_execute(self) -> GDT:
        cont = GDT_Container()
        loader = ModuleLoader.instance()
        for module in loader._cache.values():
            if any(gdt.is_writable() for gdt in module.gdo_user_settings()):
                method = settings().args_copy(self, True).env_copy(self).input('module', module.get_name)
                cont.add_field(method)
        for method in cont.all_fields():
            await method.execute()
        return cont
