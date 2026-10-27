from typing import Self


class WithHref:

    _href: str

    def href(self, href: str) -> Self:
        self._href = href
        return self

    def html_href(self) -> str:
        if href := getattr(self, '_href', None):
            return f' href="{href}"'
        return ''
