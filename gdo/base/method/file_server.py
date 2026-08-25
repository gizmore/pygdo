import mimetypes
import os
import time
from urllib.parse import unquote
from functools import lru_cache
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

    def explicitly_allowed(self, explicitly_allowed: bool = True):
        self._explicitly_allowed = explicitly_allowed
        return self


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

    @staticmethod
    @lru_cache(maxsize=65535)
    def is_forbidden(url: str) -> bool:
        # Never resolve encoded path traversal or alternate path separators.
        # ``file_server`` gets invoked before ``Application.file_path()`` and
        # must consequently make this decision from the untrusted URL alone.
        url = unquote(url).lstrip('/').replace('\\', '/')
        parts = url.split('/')
        if not url or any(part in ('', '.', '..') for part in parts):
            return True

        # Uploads are deliberately exposed only through a token/SEO file
        # route, which marks this method explicitly_allowed().  Everything in
        # protected is private configuration, logs or other service state.rest
        if parts[0] in ('files', 'protected'):
            return True

        # Application.config('dir') is a dictionary. Iterating it returns its
        # names ("logs", "config"), not directory paths ("protected/logs/").
        # Use values and compare whole path segments to avoid prefix matches
        # such as "assets-private".
        for directory in Application.config('dir').values():
            directory = directory.strip('/')
            if url == directory or url.startswith(directory + '/'):
                if directory == 'assets' and module_config_value('base', 'serve_gdo_assets'):
                    continue
                return True
        if not module_config_value('base', 'serve_gdo_assets'):
            ext = Strings.rsubstr_from(url, '.', '')
            if ext in ('js', 'css'):
                return True
        if 'secret' in url:
            return True
        if not module_config_value('base', 'serve_dot_files'):
            file = Strings.rsubstr_from(url, '/', url)
            if file.startswith('.'):
                return True
        return False

    @staticmethod
    def check_etag(file_path: str) -> bool:
        mtime = os.path.getmtime(file_path)
        etag = str(mtime) + "." + GDO_Module.CORE_REV
        last_modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(mtime))
        expires = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(mtime + 30 * 24 * 60 * 60))  # 30 days expiration
        hdr('Etag', f'"{etag}"')
        hdr('Expires', expires)
        hdr('Last-Modified', last_modified)
        return Application.get_client_header('HTTP_IF_NONE_MATCH') == etag

    def gdo_execute(self) -> GDT:
        if not hasattr(self, '_explicitly_allowed') and file_server.is_forbidden(self.get_url()):
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        file_path = self.get_path()
        if self.check_etag(file_path):
            Application.status("304 Not Modified")
            return self.empty()
        mime_type = Files.mime(file_path)
        Application.header('Content-Type', mime_type or 'application/octet-stream')
        Application.header('Content-Length', str(path.getsize(file_path)))
        return GDT_FileOut().path(file_path)
