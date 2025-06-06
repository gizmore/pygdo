import os.path

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Util import Files, href
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_Duration import GDT_Duration
from gdo.file.GDT_FileSize import GDT_FileSize
from gdo.ui.GDT_Height import GDT_Height
from gdo.ui.GDT_Width import GDT_Width


class GDO_File(GDO):
    _temp_path: str|None
    _file_data: bytes
    _no_delete: bool

    def __init__(self):
        super().__init__()
        self._no_delete = False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('file_id'),
            GDT_Name('file_name').not_null(),
            GDT_FileSize('file_size').not_null(),
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

    def get_size(self) -> int:
        return self.gdo_value('file_size')

    def get_mime(self) -> str:
        return self.gdo_val('file_mime')

    def get_path(self) -> str:
        if hasattr(self, '_temp_path'):
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
        return Application.files_path(f"gdo_file/{self.get_id()}")

    def get_preview_href(self) -> str:
        append = f'&file={self.get_id()}&token={self.gdo_hash()}'
        return href('file', 'preview', append)

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
        try:
            filename = Files.get_contents(f"{dir}name")
            return cls.blank({
                'file_name': filename,
                'file_size': str(Files.size(f"{dir}0")),
                'file_mime': Files.get_contents(f"{dir}mime"),
            }).temp_path(f"{dir}0")
        except FileNotFoundError as ex:
            Logger.exception(ex)
            return None

    @classmethod
    def from_sgi_upload(cls, file: tuple[str, str, bytes]):
        file = cls.blank({
            'file_name': file[0],
            'file_size': len(file[2]),
            'file_mime': Files.mime(file[1]),
        }).insert()
        Files.move(file[1], file.get_path())

    @classmethod
    def from_path(cls, path: str, delete: bool = False):
        file = cls.blank({
            'file_name': os.path.basename(path),
            'file_size': str(Files.size(path)),
            'file_mime': Files.mime(path),
        })
        file.temp_path(path)
        return file.no_delete(not delete)

    def gdo_after_create(self, gdo):
        dest = gdo.get_target_path()
        # Files.create_dir(dest)
        # dest += "/0"
        if hasattr(gdo, '_temp_path'):
            Files.copy(gdo._temp_path, dest)
        elif hasattr(gdo, '_file_data'):
            Files.put_contents(dest, gdo._file_data)
            gdo.set_val('file_mime', Files.mime(dest))
        gdo.set_val('file_hash', Files.md5(dest))
        gdo.save()
        gdo.clear_temp_dir()

    def gdo_after_delete(self, gdo):
        Files.delete_dir(gdo.get_target_path())

    def clear_temp_dir(self):
        if hasattr(self, '_temp_path'):
            if not self._no_delete:
                Files.delete_dir(os.path.dirname(self._temp_path))
