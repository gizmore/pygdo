import mimetypes
import os
import time
from os import path

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import hdr, Files
from gdo.core.GDT_Path import GDT_Path
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.message.GDT_HTML import GDT_HTML


class file_server(Method):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Path('_url').existing_file(),
        ]

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def get_path(self):
        return Application.file_path(self.param_val('_url').lstrip('/'))

    def gdo_execute(self) -> GDT:
        file_path = self.get_path()
        mtime = os.path.getmtime(file_path)
        etag = str(mtime) + "." + GDO_Module.CORE_REV
        last_modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(mtime))
        # expires = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(mtime + 30 * 24 * 60 * 60))  # 30 days expiration
        hdr('Etag', etag)
        hdr('Last-Modified', last_modified)
        # hdr('Expires', expires)

        if Application.get_client_header('HTTP_IF_NONE_MATCH') == etag:
            Application.status("304 Not Modified")
            return GDT_HTML()

        mime_type = Files.mime(file_path)
        Application.header('Content-Type', mime_type or 'application/octet-stream')
        Application.header('Content-Length', str(path.getsize(file_path)))
        return GDT_FileOut().path(file_path)
