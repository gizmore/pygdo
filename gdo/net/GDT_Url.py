from urllib.parse import urlparse

from gdo.core.GDT_String import GDT_String


class GDT_Url(GDT_String):
    _schemes: [str]

    def __init__(self, name):
        super().__init__(name)
        self._schemes = ['http', 'https']

    def schemes(self, schemes):
        self._schemes = schemes
        return self

    def to_value(self, val: str):
        if val is None:
            return None
        return urlparse(val)

    def validate(self, value):
        if not super().validate(value):
            return False
        if value is None:
            return True
        if hasattr(self, '_schemes'):
            if not self.validate_scheme(value):
                return False
        return True

    def validate_scheme(self, url):
        return True
