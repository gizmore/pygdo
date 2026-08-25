from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.ui.GDT_Link import GDT_Link


class seo_files(MethodQueryTable):
    """Staff overview of public SEO-path-to-upload mappings."""

    def gdo_table(self) -> GDO:
        return GDO_SeoFile.table()

    def gdo_table_headers(self) -> list[GDT]:
        table = self.gdo_table()
        return [
            table.column('sf_url'),
            GDT_Link('view').label('sf_file'),
        ]

    def render_view(self, gdt: GDT_Link, gdo: GDO_SeoFile):
        file = gdo.get_file()
        return gdt.href(file.get_preview_href()).text_raw(file.get_name()).render()
