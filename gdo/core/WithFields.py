from typing import Iterator

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Render import Mode


class WithFields:

    _fields: list[GDT]

    def get_fields(self) -> list[GDT]:
        # if not hasattr(self, '_fields'):
        #     self._fields = []
        return self._fields

    def add_field(self, field):
        self._fields.append(field)
        return self

    def add_fields(self, *fields):
        self._fields.extend(fields)
        return self

    def get_field(self, name: str):
        for gdt in self._fields:
            if gdt.get_name() == name:
                return gdt
            if hasattr(gdt, 'get_field'):
                if gdt2 := gdt.get_field(name):
                    return gdt2
        return None

    def has_fields(self) -> bool:
        return True

    # def fields(self) -> list[GDT]:
    #     return self._fields if hasattr(self, '_fields') else GDO.EMPTY_LIST

    def all_fields(self) -> Iterator[GDT]:
        """
        Returns an iterator that iterates over all nested fields.
        """
        # if self.has_fields():
        for gdt in self._fields:
            yield gdt
            if hasattr(gdt, '_fields'):
                yield from gdt._fields

    # def clear(self):
    #     self.get_fields().clear()

    ##########
    # Render #
    ##########
    def render(self, mode: Mode = Mode.render_html):
        if mode == Mode.render_json:
            return self.render_json()
        return self.render_fields(mode)

    def render_html(self) -> str:
        return self.render_fields()

    def render_json(self):
        out = {}
        for gdt in self.all_fields():
            out.update(gdt.render_json())
        return out

    def render_fields(self, mode: Mode = Mode.render_html) -> str:
        if not hasattr(self, '_fields'):
            return ''
        return " ".join([gdt.render(mode) for gdt in self._fields])
