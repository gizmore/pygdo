
class WithSize:
    _width: str
    _height: str

    def width(self, width: str):
        self._width = width
        return self

    def height(self, height: str):
        self._height = height
        return self
