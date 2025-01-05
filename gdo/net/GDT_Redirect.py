from gdo.base.Application import Application
from gdo.ui.GDT_Panel import GDT_Panel
from gdo.ui.WithHREF import WithHREF


class GDT_Redirect(WithHREF, GDT_Panel):

    def render_html(self):
        Application.status("303 See Other")
        Application.header('Location', self._href)
        return super().render_html()
