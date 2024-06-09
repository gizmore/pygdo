class WithFields:
    _fields: list

    def add_field(self, *fields):
        if not hasattr(self, '_fields'):
            self._fields = []
        self._fields.extend(fields)
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
        if hasattr(self, '_fields'):
            return self._fields
        return []

    def all_fields(self):
        """
        Returns an iterator that iterates over all nested fields.
        """
        if self.has_fields():
            for gdt in self.fields():
                yield gdt
                if gdt.has_fields():
                    yield from gdt.all_fields()

    ##########
    # Render #
    ##########
    def render_txt(self) -> str:
        output = ""
        if hasattr(self, '_fields'):
            for gdt in self._fields:
                output += gdt.render_txt()
        return output

    def render_cli(self) -> str:
        output = ""
        if hasattr(self, '_fields'):
            for gdt in self._fields:
                output += gdt.render_cli()
        return output

    def render_irc(self) -> str:
        output = ""
        if hasattr(self, '_fields'):
            for gdt in self._fields:
                output += gdt.render_irc()
        return output

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
