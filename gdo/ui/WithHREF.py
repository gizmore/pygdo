from gdo.base.Util import html


class WithHREF:
    _href: str

    def href(self, href: str):
        self._href = href
        return self

    def render_href(self) -> str:
        return html(self._href)
