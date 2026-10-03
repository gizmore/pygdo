from typing import Iterator

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.core.GDT_Field import GDT_Field


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
        for gdt in self.get_fields():
            # ``render_json`` bypasses ``Method.render``.  A container may
            # contain a method (for example an overview embedding tables),
            # whose result must be rendered in JSON mode rather than reduced
            # to the method name.
            value = gdt.render(Mode.render_json)
            if isinstance(value, dict):
                # Methods and explicitly named composite fields own a JSON
                # object.  Keeping that object under their name prevents two
                # embedded tables from both overwriting the generic ``table``
                # key in their parent container.
                if not isinstance(gdt, GDT_Field) and type(gdt).get_name is not GDT.get_name:
                    out[gdt.get_name()] = value
                    continue
                for key, item in value.items():
                    # Anonymous display fields such as links have no stable
                    # field name.  JSON object keys cannot be ``None``.
                    out[key or gdt.get_name() or gdt.__class__.__name__] = item
            else:
                # Fields normally provide a name/value mapping, but methods,
                # display snippets and other GDTs may render a scalar.
                # Preserve them instead of assuming ``dict.update(value)``.
                out[gdt.get_name() or gdt.__class__.__name__] = value
        return out

    def render_fields(self, mode: Mode = Mode.render_html) -> str:
        if not hasattr(self, '_fields'):
            return ''
        return " ".join([gdt.render(mode) for gdt in self._fields])
