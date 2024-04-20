import psutil

from gdo.base.GDO_Module import GDO_Module
from gdo.base.Util import Files
from gdo.core.GDT_String import GDT_String
from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Perf(GDT_Panel):

    def __init__(self):
        super().__init__()

    def get_perf(self):
        mem = psutil.Process().memory_info()
        return GDT_Bar().horizontal().add_field(
            GDT_String('version').text('perf_version', [GDO_Module.CORE_REV]),
            GDT_String('cpu').text('perf_cpu', [str(psutil.cpu_percent())]),
            GDT_String('mem').text('perf_mem', [Files.human_file_size(mem.rss)]),
        )

    def render_cli(self):
        return self.get_perf().render_cli()
