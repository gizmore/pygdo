from gdo.core.GDT_Container import GDT_Container
from gdo.ui.GDT_Image import GDT_Image


class GDT_Card(GDT_Container):
    _image: GDT_Image

    def image(self, image: GDT_Image):
        self._image = image
        return self
