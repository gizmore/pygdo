from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_Int import GDT_Int
from gdo.core.GDT_String import GDT_String


class GDT_ProcessLoad(GDT_Float):
    """A sortable percentage used by the read-only process table."""

    def is_orderable(self) -> bool:
        return True

    def default_order(self) -> str:
        return 'DESC'


class GDO_Process(GDO):
    """Ephemeral local process information; it is never persisted."""

    def gdo_cached(self) -> bool:
        return False

    def gdo_can_persist(self) -> bool:
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_Int('proc_pid').primary(),
            GDT_ProcessLoad('proc_load').precision(1),
            GDT_ProcessLoad('proc_memory').precision(1),
            GDT_String('proc_command').maxlen(255),
        ]

    def get_name(self) -> str:
        return self.gdo_val('proc_command')
