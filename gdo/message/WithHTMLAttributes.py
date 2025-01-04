from gdo.base.Util import html


class WithHTMLAttributes:

    _attrs: dict[str, str]

    def get_attrs(self) -> dict[str, str]:
        if not hasattr(self, '_attrs'):
            self._attrs = {}
        return self._attrs

    def attr(self, key: str, value: str = None):
        if value is None:
            return self.get_attrs()[key]
        self.get_attrs()[key] = value
        return self

    def html_attrs(self) -> str:
        out = ""
        for key, value in self.get_attrs().items():
            out += f' {key}="{html(value)}"'
        return out.strip()
