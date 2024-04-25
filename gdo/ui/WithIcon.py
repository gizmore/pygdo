class WithIcon:

    @classmethod
    def render_icon(cls, name: str, color: str = 'gold', size: str='14px'):
        return cls().icon(name, color, size).render()

    _icon_name: str
    _icon_color: str
    _icon_size: str

    def icon(self, name: str, color: str='gold', size='14px'):
        self._icon_name = name
        self._icon_color = color
        self._icon_size = size
        return self

    def icon_name(self, name: str):
        self._icon_name = name
        return self

    def icon_color(self, color: str):
        self._icon_color = color
        return self

    def icon_size(self, size: str):
        self._icon_size = size
        return self

