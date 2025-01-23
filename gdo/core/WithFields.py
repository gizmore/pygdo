from gdo.base.GDT import GDT
from gdo.base.Render import Mode


class WithFields:
    _fields: list[GDT]

    def get_fields(self) -> list[GDT]:
        if not hasattr(self, '_fields'):
            self._fields = []
        return self._fields

    def add_field(self, *fields):
        self.get_fields().extend(fields)
        return self

    def get_field(self, name: str):
        for gdt in self.fields():
            if gdt.get_name() == name:
                return gdt
            if gdt.has_fields():
                if gdt2 := gdt.get_field(name):
                    return gdt2

    def has_fields(self) -> bool:
        return True

    def fields(self) -> list[GDT]:
        if hasattr(self, '_fields'):
            return self._fields
        return []

    def all_fields(self) -> list[GDT]:
        """
        Returns an iterator that iterates over all nested fields.
        """
        if self.has_fields():
            for gdt in self.fields():
                yield gdt
                if gdt.has_fields():
                    yield from gdt.all_fields()

    def clear(self):
        self.get_fields().clear()

    ##########
    # Render #
    ##########
    def render(self, mode: Mode = Mode.HTML):
        return self.render_fields(mode)

    def render_fields(self, mode: Mode = Mode.HTML):
        output = ""
        if hasattr(self, '_fields'):
            for gdt in self._fields:
                output += gdt.render(mode)
        return output
