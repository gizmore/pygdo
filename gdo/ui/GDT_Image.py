from gdo.base.GDT import GDT
from gdo.ui.WithHREF import WithHREF


class GDT_Image(WithHREF, GDT):
    _alt_key: str
    _alt_args: list

    def __init__(self):
        super().__init__()

    def alternate(self, alt_key: str, alt_args: list = None):
        self._alt_key = alt_key
        self._alt_args = alt_args
        return self

    ##########
    # Render #
    ##########
    def render_txt(self) -> str:
        return self.render_alternate()

    def render_alternate(self):
        pass
    