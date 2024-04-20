from gdo.base.Util import Arrays


class WithFields:
    _fields: list

    def add_field(self, *fields):
        if not hasattr(self, '_fields'):
            self._fields = []
        for gdt in fields:
            self._fields.append(gdt)
        return self

    def get_field(self, name: str):
        for gdt in self._fields:
            if gdt.get_name() == name:
                return gdt
            if gdt.has_fields():
                gdt2 = gdt.get_field_named(name)
                if gdt2:
                    return gdt2
        return None

    def has_fields(self) -> bool:
        return True

    def fields(self) -> list:
        return self._fields

    def all_fields(self):
        """
        Returns an iterator that iterates over all nested fields.
        """
        if self.has_fields():
            for gdt in self._fields:
                yield gdt
                if gdt.has_fields():
                    yield from gdt.all_fields()

    ##########
    # Render #
    ##########

    def render(self) -> str | list:
        pass

    def render_html(self) -> str:
        output = ""
        if hasattr(self, '_fields'):
            for gdt in self._fields:
                output += gdt.render_html()
        return output

    def render_form(self) -> str:
        output = ""
        if hasattr(self, '_fields'):
            for gdt in self._fields:
                output += gdt.render_form()
        return output

