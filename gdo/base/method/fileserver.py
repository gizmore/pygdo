import mimetypes
from os import path

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.net.GDT_Url import GDT_Url


class fileserver(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Url('_url').not_null(),
        ]

    def get_path(self):
        return self.param_val('_url')

    def gdo_execute(self):
        path_ = self.get_path()
        mime_type, _ = mimetypes.guess_type(path_)
        Application.header('Content-Type', mime_type)
        Application.header('Content-Length', str(path.getsize(path_)))
        return GDT_FileOut().path(path_)
