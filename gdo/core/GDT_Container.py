from gdo.base.GDT import GDT
from gdo.core.WithFields import WithFields
from gdo.ui.WithFlow import WithFlow


class GDT_Container(WithFlow, WithFields, GDT):

    __slots__ = (
        '_fields',
    )

    def __init__(self):
        super().__init__()
        self._fields = []
        self.horizontal()

    def render_html(self) -> str:
        return f'<div class="gdt-container {self.render_class()}">{self.render_fields()}</div>\n'
