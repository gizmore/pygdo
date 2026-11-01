from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Char import GDT_Char
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text


class GDO_LangText(GDO):
    """Reusable translations indexed by namespace, resource key and ISO."""

    def gdo_cached(self) -> bool:
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_String('lt_namespace').maxlen(64).ascii().primary(),
            GDT_String('lt_key').maxlen(128).ascii().primary(),
            GDT_Char('lt_iso').maxlen(2).ascii().case_s().primary(),
            GDT_Text('lt_text').not_null(),
        ]

    @classmethod
    def put(cls, namespace: str, key: str, iso: str, text: str):
        return cls.blank({'lt_namespace': namespace, 'lt_key': key,
                          'lt_iso': iso, 'lt_text': text}).replace()

    @classmethod
    def lookup(cls, namespace: str, key: str, iso: str, fallback: str = 'en') -> str | None:
        for language in dict.fromkeys((iso, fallback)):
            if language and (row := cls.table().get_by_id(namespace, key, language)):
                return row.gdo_val('lt_text')
        return None
