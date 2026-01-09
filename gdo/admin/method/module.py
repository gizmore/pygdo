from gdo.admin.method.configure import configure
from gdo.admin.method.install import install
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Container import GDT_Container


class module(Method):

    async def gdo_execute(self) -> GDT:
        return GDT_Container().vertical().add_fields(await self.submethod(configure), await self.submethod(install))

    async def submethod(self, klass: type[Method]):
        method = klass().args_copy(self).env_copy(self)
        return await method.execute()
