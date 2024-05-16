class WithFlow:
    """
    Adds a flow attrivute to GDTs.
    Horizontal or vertical.
    """

    _flow_horz: bool

    def horizontal(self, horizontal: bool = True):
        self._flow_horz = horizontal
        return self

    def vertical(self, vertical: bool = True):
        return self.horizontal(not vertical)

    def is_horizontal(self) -> bool:
        return self._flow_horz

    def is_vertical(self) -> bool:
        return not self._flow_horz

    def render_class(self) -> str:
        return 'gdt-row' if self.is_horizontal() else 'gdt-col'
