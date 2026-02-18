from gdo.admin.GDT_Module import GDT_Module
from gdo.admin.method.configure import configure
from gdo.admin.method.install import install
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import sitename
from gdo.core.GDT_Container import GDT_Container


class module(Method):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null(),
        ]

    async def submethod(self, klass: type[Method]):
        method = klass().args_copy(self).env_copy(self)
        return await method.execute()

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_render_descr(self) -> str:
        m = self.get_module()
        return self.t('md_admin_module', (m.render_name(), sitename()))

    def gdo_render_title(self) -> str:
        m = self.get_module()
        return self.t('mt_admin_module', (m.render_name(),))

    async def gdo_execute(self) -> GDT:
        return GDT_Container().vertical().add_fields(
            await self.submethod(install),
            await self.submethod(configure))
