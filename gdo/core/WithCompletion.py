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
            initial = self.gdo_completion_initial()
            return f' gdo-completion="{self._completion_href}" gdo-completion-data=\'{jsn(self._completion_data).decode()}\' gdo-completion-data2=\'{jsn(self.gdo_completion_data()).decode()}\' gdo-completion-initial=\'{jsn(initial).decode()}\''
        return ''

    def gdo_completion_data(self) -> dict[str, str]:
        return {}

    def gdo_completion_initial(self) -> dict[str, str] | None:
        """Describe the current value for Select2's initial selection."""
        value = self.get_val()
        if value is None:
            return None
        resolved = self.get_value()
        if hasattr(resolved, 'get_id'):
            # Completion endpoints commonly submit a human-resolvable value
            # instead of the database identifier.  Preserve that value for
            # the input while Select2 uses the stable object id internally.
            var = resolved.get_name_sid() if hasattr(resolved, 'get_name_sid') else value
            return {
                'id': resolved.get_id(),
                'var': var,
                'display_var': resolved.render_name(),
            }
        return {
            'id': value,
            'var': value,
            'display_var': value,
        }
