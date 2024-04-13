class WithFlow:
    """
    Adds a flow attrivute to GDTs.
    Horizontal or vertical.
    """

    _flow_horizontal: bool

    def horz(self, horizontal: bool = True):
        self._flow_horizontal = horizontal
        return self

    def vert(self, vertical: bool = True):
        return self.horz(not vertical)

    def is_horizontal(self) -> bool:
        return self._flow_horizontal

    def is_vertical(self) -> bool:
        return not self._flow_horizontal

    def render_class(self) -> str:
        return 'gdt-col' if self.is_horizontal() else 'gdt-row'
