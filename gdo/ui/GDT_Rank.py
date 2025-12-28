from gdo.core.GDT_UInt import GDT_UInt


class GDT_Rank(GDT_UInt):

    _rank: int

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('trophy')
        self.bytes(4)
        self._rank = 1

    def render_cell(self) -> str:
        back = str(self._rank)
        self._rank += 1
        return back
