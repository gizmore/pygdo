from gdo.base import module_base
from gdo.base.GDT import GDT
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Perf(GDT_Panel):

    def __init__(self):
        super().__init__()

    def render_cli(self):
        v = module_base.instance().CORE_VERSION
        mem = 100
        return f"PyGDOv{v} - {mem} bytes used - {GDT.GDT_COUNT} GDTs"
