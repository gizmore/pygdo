from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.base.GDO import GDO

class WithGDO:
    _gdo: 'GDO'

    def gdo(self, gdo: 'GDO'):
        self._gdo = gdo
        return self
