from gdo.base.Result import ResultType
from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect
from gdo.date.GDO_Timezone import GDO_Timezone


class GDT_Timezone(GDT_ObjectSelect):

    def __init__(self, name: str):
        super().__init__(name)
        self.table(GDO_Timezone.table())

    def gdo_choices(self) -> dict:
        return self._table.select('tz_name').exec().iter(ResultType.ROW).fetch_all_dict()
