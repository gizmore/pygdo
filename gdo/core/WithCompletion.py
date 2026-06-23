from typing import Self

from gdo.base.Util import jsn


class WithCompletion:
    _completion_href: str
    _completion_data: dict[str, str] | None

    def completion(self, href: str, data: dict[str, str] = {}) -> Self:
        self._completion_href = href
        self._completion_data = data
        return self

    def has_completion(self) -> bool:
        return hasattr(self, '_completion_href') and self._completion_href is not None

    def html_completion(self) -> str:
        if self.has_completion():
            return f' gdo-completion="{self._completion_href}" gdo-completion-data=\'{jsn(self._completion_data).decode()}\' gdo-completion-data2=\'{jsn(self.gdo_completion_data()).decode()}\''
        return ''

    def gdo_completion_data(self) -> dict[str, str]:
        return {}
