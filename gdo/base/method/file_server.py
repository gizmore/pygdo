import mimetypes
import os
import time
import urllib
from os import path

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import hdr, Files, msg, module_config_value, Strings
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

    def get_url(self) -> str:
        return self.param_val('_url').lstrip('/')

    def get_path(self):
        return Application.file_path(self.get_url())

    def gdo_execute(self) -> GDT:
        url = self.get_url()
        dir = Strings.substr_to(url, '/', None)
        if not dir:
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        if dir in ('bin', 'cache', 'DEV', 'files', 'files_test', 'gdotest', 'protected', 'temp'):
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        if not module_config_value('base', 'serve_gdo_assets'):
            ext = Strings.rsubstr_from(url, '.', '')
            if ext in ('js', 'css'):
                Application.status('403 Forbidden')
                return self.err('err_file_forbidden')
        if 'secret' in url:
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        if not module_config_value('base', 'serve_dot_files'):
            file = Strings.rsubstr_from(url, '/', url)
            if file.startswith('.'):
                Application.status('403 Forbidden')
                return self.err('err_file_forbidden')

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
