from gdo.base.GDT import GDT


class GDT_List(GDT):
    """
    A list that can be gdopack serialized.
    """

    _items: list[any]

    __slots__ = (
        '_items',
    )

    def __init__(self, *items):
        super().__init__()
        self._items = list(items)

    def gdo_redis_fields(self) -> list[str]:
        return [
            '_items',
        ]

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __setitem__(self, index, value):
        self._items[index] = value

    def __len__(self):
        return len(self._items)

    def append(self, item):
        self._items.append(item)

    def reverse(self) -> list[any]:
        return self._items.reverse()
