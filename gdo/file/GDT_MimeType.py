from gdo.core.GDT_Enum import GDT_Enum


class GDT_MimeType(GDT_Enum):
    IMAGE_TYPES = {
        'image/png': 'PNG Image',
        'image/jpeg': 'JPEG Image',
    }

    def gdo_choices(self) -> dict:
        return self.IMAGE_TYPES
