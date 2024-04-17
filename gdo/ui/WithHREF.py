class WithHREF:
    _href: str

    def href(self, href: str):
        self._href = href
        return self

    def render_href(self):
        return self._href
