import mimetypes
import os
import time
from os import path

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import hdr
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Path import GDT_Path
from gdo.core.GDT_String import GDT_String
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.ui.GDT_HTML import GDT_HTML


class file_server(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Path('_url').existing_file(),
        ]

    def cli_trigger(self) -> str:
        return ""

    def get_path(self):
        return self.param_val('_url')

    def gdo_execute(self):
        file_path = self.get_path()
        stat_info = os.stat(file_path)
        mtime = stat_info.st_mtime
        etag = GDT_MD5.hash_for_file(file_path)
        last_modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(mtime))
        expires = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(mtime + 30 * 24 * 60 * 60))  # 30 days expiration
        hdr('Etag', etag)
        hdr('Last-Modified', last_modified)
        hdr('Expires', expires)

        # Application.get_client_header('HTTP_IF_MODIFIED_SINCE')
        if Application.get_client_header('HTTP_IF_NONE_MATCH') == etag:
            Application.status("304 Not Modified")
            return GDT_HTML()

        path_ = self.get_path()
        mime_type, _ = mimetypes.guess_type(path_)
        Application.header('Content-Type', mime_type)
        Application.header('Content-Length', str(path.getsize(path_)))
        return GDT_FileOut().path(path_)
