import psutil

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Duration import GDT_Duration
from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Divider import GDT_Divider
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Perf(GDT_Panel):

    def __init__(self):
        super().__init__()

    def get_perf(self):
        user = GDO_User.current()
        mem = psutil.Process().memory_info()
        stor = Application.STORAGE
        return GDT_Bar().horizontal().add_field(
            GDT_String('version').text('perf_version', [GDO_Module.CORE_REV]),
            GDT_Divider(),
            GDT_String('user').text('perf_user', [user.render_name(), user.get_id()]),
            GDT_Divider(),
            GDT_String('cpu').text('perf_cpu', [str(psutil.cpu_percent())]),
            GDT_Divider(),
            GDT_String('mem').text('perf_mem', [Files.human_file_size(mem.rss)]),
            GDT_Divider(),
            GDT_String('db').text('perf_db', [stor.db_reads, stor.db_writes, stor.db_queries]),
            GDT_Divider(),
            GDT_String('code').text('perf_code', [GDT.GDT_COUNT, GDT.GDT_MAX, GDO.GDO_COUNT, GDO.GDO_MAX]),
            GDT_Divider(),
            GDT_Duration('time').initial_value(Application.request_time()),
        )

    def render_html(self):
        self.text_raw(self.get_perf().render_html(), False)
        return super().render_html()

    def render_cli(self):
        return self.get_perf().render_cli()
