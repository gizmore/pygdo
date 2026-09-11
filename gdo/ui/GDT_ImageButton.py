from gdo.base.Render import Mode
from gdo.base.Util import html
from gdo.ui.WithImage import WithImage
from gdo.ui.GDT_Button import GDT_Button


class GDT_ImageButton(WithImage, GDT_Button):
    """Native submit button: image plus a visible, accessible text label."""

    def render(self, mode: Mode = Mode.render_html):
        return self.render_html() if mode.is_html() else self.render_text(mode)

    def render_html(self):
        image = self._image.render_html() if self.has_image() else ''
        disabled = ' disabled aria-disabled="true"' if self.is_disabled() else ''
        return (f'<button{self.html_attrs()} type="submit" name="{html(self.get_name())}" '
                f'value="1"{disabled}>{image}<span>{self.render_text()}</span></button>')
