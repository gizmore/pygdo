import json

from gdo.core.GDT_String import GDT_String


class GDT_JSON(GDT_String):
    """A JSON document stored in a native JSON database column."""

    def gdo_column_define(self) -> str:
        return f"{self.get_name()} JSON{self.gdo_column_define_null()}"

    def to_val(self, value) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))

    def to_value(self, val: str):
        return json.loads(val) if val else None

    def validate(self, val: str | None) -> bool:
        if not super().validate(val):
            return False
        if not val:
            return True
        try:
            json.loads(val)
        except (TypeError, json.JSONDecodeError):
            return self.error('err_json_invalid')
        return True
