from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Token import GDT_Token
from gdo.file.method.preview import preview


class preview_session(preview):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_String('path').not_null(),
            GDT_Token('token').not_null(),
        ]

    def get_path(self) -> str:
        return self.param_value('path')

    def get_temp_dir(self):
        sessid = self._env_session.get_id()
        files_dir = Application.config('file.directory')
        return Application.temp_path(f"{files_dir}{self.get_path()}/{sessid}/")

    def get_file(self) -> GDO_File:
        dir = self.get_temp_dir()
        if not Files.is_dir(dir):
            return None
        return GDO_File.from_dir(dir)
