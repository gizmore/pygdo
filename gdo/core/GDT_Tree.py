from functools import lru_cache

from gdo.base.GDT import GDT
from gdo.core.GDT_Composite import GDT_Composite
from gdo.core.GDT_UInt import GDT_UInt


class GDT_Tree(GDT_Composite):
    """A tree interval represented by unsigned ``left`` and ``right`` bounds.

    A column named ``node`` expands to the database columns ``node_left`` and
    ``node_right``.  It deliberately does not impose a particular tree
    algorithm; callers may use it for nested sets, intervals, or another
    left/right tree representation.
    """

    def left_key(self) -> str:
        return f'{self._name}_left'

    def right_key(self) -> str:
        return f'{self._name}_right'

    @lru_cache
    def gdo_components(self) -> list[GDT]:
        return [
            self,
            GDT_UInt(self.left_key()).not_null(self.is_not_null()),
            GDT_UInt(self.right_key()).not_null(self.is_not_null()),
        ]

    def not_null(self, not_null: bool = True):
        super().not_null(not_null)
        self.gdo_components.cache_clear()
        return self

    def get_left(self) -> int | None:
        return self._gdo.gdo_value(self.left_key())

    def get_right(self) -> int | None:
        return self._gdo.gdo_value(self.right_key())

    def get_value(self) -> tuple[int | None, int | None]:
        return self.get_left(), self.get_right()

    def set_left(self, left: int | None):
        self._gdo.set_value(self.left_key(), left)
        return self

    def set_right(self, right: int | None):
        self._gdo.set_value(self.right_key(), right)
        return self

    def set(self, left: int | tuple[int, int], right: int | None = None):
        if right is None:
            left, right = left
        return self.set_left(left).set_right(right)

    def value(self, value: tuple[int, int]):
        return self.set(value)
