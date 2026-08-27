from gdo.base.Render import Mode
from gdo.base.Util import Files
from gdo.core.GDT_UInt import GDT_UInt


class GDT_FileSize(GDT_UInt):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('database')

    def to_value(self, val: str):
        return Files.human_to_file_size(val)

    def to_val(self, value) -> str:
        return Files.human_file_size(value)

    def render_html(self, mode: Mode = Mode.render_html):
        return self.to_val(self.get_value())
