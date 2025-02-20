from gdo.account.method.settings import settings
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Container import GDT_Container
from gdo.ui.GDT_Bar import GDT_Bar


class all_settings(Method):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    async def gdo_execute(self) -> GDT:
        cont = GDT_Container()
        loader = ModuleLoader.instance()
        for module in loader._cache.values():
            for _ in module.all_user_settings():
                method = settings().args_copy(self).env_copy(self).input('module', module.get_name())
                cont.add_field(method)
                break
        for method in cont.all_fields():
            await method.execute()
        return cont
