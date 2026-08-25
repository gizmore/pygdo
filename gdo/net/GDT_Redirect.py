from gdo.base.Application import Application
from gdo.ui.GDT_Panel import GDT_Panel
from gdo.ui.WithHREF import WithHREF


class GDT_Redirect(WithHREF, GDT_Panel):

    def href(self, href: str):
        super().href(href)
        # WSGI collects response headers before the page is rendered. Setting
        # these in render_html() therefore showed a redirect panel but sent a
        # regular 200 response without a Location header.
        if Application.IS_HTTP:
            Application.status("303 See Other")
            Application.header('Location', href)
        return self
