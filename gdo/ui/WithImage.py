from gdo.base.GDT import GDT


class WithImage:
    _image: GDT

    def image(self, image: GDT):
        self._image = image
        return self

    def has_image(self) -> bool:
        return getattr(self, '_image', None) is not None
