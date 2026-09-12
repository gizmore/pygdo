from gdo.base.Render import Mode
from gdo.base.Util import html
from gdo.core.GDT_Select import GDT_Select
from gdo.ui.GDT_Icon import GDT_Icon
from gdo.ui.IconProvider import IconProvider
from gdo.ui.IconUTF8 import IconUTF8


class _IconChoice(GDT_Icon):
    """A named icon as it appears in an icon select option."""

    def render_html(self) -> str:
        return self.render_icon(Mode.render_html)

    def render_list(self) -> str:
        return f'{self.render_html()} {self.get_name()}'


class GDT_IconSelect(GDT_Select):
    """A nullable database field for choosing one registered UI icon."""

    def __init__(self, name: str = 'icon'):
        super().__init__(name)
        self.ascii().maxlen(64)
        self.attr('data-gdt-icon-select', '1')

    @classmethod
    def icon_names(cls) -> list[str]:
        names = set(IconUTF8.MAP())
        for provider in IconProvider.PROVIDERS:
            names.update(provider.MAP())
        return sorted(names)

    def gdo_choices(self) -> dict:
        return {name: _IconChoice(name) for name in self.icon_names()}

    def html_option_attrs(self, key: str, choice) -> str:
        if isinstance(choice, _IconChoice):
            return (f' data-icon-html="{html(choice.render_html())}"'
                    f' data-icon-label="{html(choice.get_name())}"')
        return self.EMPTY_STR

    def to_value(self, val: str):
        """Persist the icon name, rather than the display-only icon object."""
        if val == '':
            return ''
        return val if val in self.init_choices() else None

    def to_val(self, value) -> str:
        if value is None:
            return None
        value = str(value)
        return value if value in self.init_choices() else None
