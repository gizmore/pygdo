import mimetypes
import os.path

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import Files
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_Duration import GDT_Duration
from gdo.ui.GDT_Height import GDT_Height
from gdo.ui.GDT_Width import GDT_Width


class GDO_File(GDO):
    _temp_path: str
    _file_data: bytes
    _no_delete: bool

    def __init__(self):
        super().__init__()
        self._no_delete = False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('file_id'),
            GDT_Name('file_name').not_null(),
            GDT_UInt('file_size').not_null(),
            GDT_String('file_mime').not_null(),
            GDT_MD5('file_hash'),
            GDT_Duration('file_duration'),
            GDT_Width('file_width'),
            GDT_Height('file_height'),
            GDT_Created('file_created'),
            GDT_Creator('file_creator'),
        ]

    def get_name(self):
        return self.gdo_val('file_name')

    def get_mime(self) -> str:
        return self.gdo_val('file_mime')

    def get_path(self) -> str:
        if self._temp_path:
            return self._temp_path
        return self.get_target_path()

    def is_image(self) -> bool:
        from gdo.file.GDT_MimeType import GDT_MimeType
        return self.get_mime() in GDT_MimeType.IMAGE_TYPES

    def temp_path(self, path: str):
        self._temp_path = path
        return self

    def no_delete(self, no_delete: bool = True):
        self._no_delete = no_delete
        return self

    def get_target_path(self) -> str:
        return Application.file_path(f"files/{self.get_id()}")

    @classmethod
    def from_memory(cls, file_data: tuple):
        key, filename, data = file_data
        file = cls.blank({
            'file_name': filename,
            'file_size': str(len(data)),
        })
        file._file_data = data
        return file

    @classmethod
    def from_dir(cls, dir: str):
        filename = Files.get_contents(f"{dir}name")
        file = cls.blank({
            'file_name': filename,
            'file_size': str(Files.size(f"{dir}0")),
            'file_mime': Files.get_contents(f"{dir}mime"),
        })
        file.temp_path(f"{dir}/0")
        return file

    @classmethod
    def from_path(cls, path: str, delete: bool = False):
        mime_type = Files.mime(path)
        file = cls.blank({
            'file_name': os.path.basename(path),
            'file_size': str(Files.size(path)),
            'file_mime': mime_type,
        })
        file.temp_path(path)
        return file.no_delete(not delete)

    def gdo_after_create(self, gdo):
        dest = gdo.get_target_path()
        if hasattr(gdo, '_temp_path'):
            Files.copy(gdo._temp_path, dest)
        elif hasattr(gdo, '_file_data'):
            Files.put_contents(dest, gdo._file_data)
            gdo.set_val('file_mime', Files.mime(dest))
        gdo.set_val('file_hash', Files.md5(dest))
        gdo.save()
        gdo.clear_temp_dir()

    def clear_temp_dir(self):
        if hasattr(self, '_temp_path'):
            if not self._no_delete:
                Files.delete_dir(os.path.dirname(self._temp_path))
