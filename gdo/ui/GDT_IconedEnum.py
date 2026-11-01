from gdo.base.Render import Mode
from gdo.base.Application import Application
from gdo.base.Util import html
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Template import tpl
from gdo.ui.IconProvider import IconProvider


class GDT_IconedEnum(GDT_Enum):
    """An enum whose selected value supplies its icon."""

    def __init__(self, name: str):
        super().__init__(name)
        self._choice_icons = {}
        self.attr('data-iconed-enum', '1')

    def icons(self, icons: dict[str, str]):
        self._choice_icons = dict(icons)
        return self

    def choice_icon(self, key: str, mode: Mode = Mode.render_html) -> str:
        name = self._choice_icons.get(key)
        return IconProvider.display_icon(name, mode) if name else ''

    def render_icon(self, mode: Mode) -> str:
        return self.choice_icon(self.get_val(), mode)

    def html_option_attrs(self, key: str, choice) -> str:
        return f' data-icon-html="{html(self.choice_icon(key))}"'

    def render_form(self):
        if Application.IS_HTTP:
            from gdo.ui.module_ui import module_ui
            ui = module_ui.instance()
            path = ui.www_path('js/pygdo-ui.js')
            if not any(asset.split('?', 1)[0] == path for asset in ui.gdt_page()._js):
                ui.add_js('js/pygdo-ui.js')
        return tpl('ui', 'form_iconed_enum.html', {'field': self, 'Mode': Mode})

    def render_cell(self) -> str:
        return self.render_icon(Mode.render_html) + super().render_cell()
