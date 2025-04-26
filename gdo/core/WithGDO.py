from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from gdo.base.GDO import GDO

class WithGDO:
    _gdo: 'GDO'

    def gdo(self, gdo: 'GDO') -> Self:
        self._gdo = gdo
        return self
