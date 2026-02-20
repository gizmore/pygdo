from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_File import GDO_File
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.ui.GDT_Link import GDT_Link


class files(MethodQueryTable):

    def gdo_table(self) -> GDO:
        return GDO_File.table()

    def gdo_table_headers(self) -> list[GDT]:
        t = self.gdo_table()
        return [
            t.column('file_id'),
            GDT_Link('view').label('file_name'),
            t.column('file_size'),
        ]

    def render_view(self, gdt: GDT_Link, gdo: GDO_File):
        return gdt.href(gdo.get_preview_href()).text_raw(gdo.get_name()).render()
