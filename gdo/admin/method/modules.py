import functools

from gdo.base.GDO import GDO
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render, Mode
from gdo.base.Result import Result
from gdo.base.ResultArray import ResultArray
from gdo.base.Trans import Trans
from gdo.core.GDT_Bool import GDT_Bool
from gdo.table.MethodTable import MethodTable


class modules(MethodTable):
    _n: int
    """
    Overview over modules
    """

    def gdo_trigger(self) -> str:
        return 'modules'

    def gdo_table(self) -> GDO:
        return GDO_Module.table()

    def gdo_table_result(self) -> Result:
        return ResultArray(self.get_modules(), self.gdo_table())

    def gdo_paginated(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        Trans.reload()
        mods = self.get_modules()
        self._n = 0
        return super().gdo_execute()

    @functools.cache
    def get_modules(self) -> list[GDO_Module]:
        loader = ModuleLoader.instance()
        mods = loader.load_modules_fs()
        return list(mods.values())

    def render_txt(self) -> str:
        gdo = self._gdo
        self._n += 1
        return f'{self._n}-{gdo.render_name()}'

    def render_cli(self) -> str:
        gdo = self._gdo
        self._n += 1
        n = Render.bold(str(self._n), Mode.CLI)
        name = gdo.render_name()
        name = Render.green(name, Mode.CLI) if gdo.installed() else name
        return f'{name}'

    def render_module_enabled(self, gdt: GDT_Bool) -> str:
        if gdt._gdo.is_persisted():
            return 'Y' if gdt._val == '1' else 'N'
        return ''
