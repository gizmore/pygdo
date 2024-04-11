

class WithFields:

    _fields: []

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
