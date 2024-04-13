from gdo.base.Render import Mode


class WithMode:
    """
    Adds mode field to GDT.
    Used by GDT_Response and GDT_Result
    """
    _mode: Mode

    def mode(self, mode: Mode):
        self._mode = mode
        return self

    def render_nil(self) -> str:
        return ''
