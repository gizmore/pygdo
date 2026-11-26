import mimetypes
import os
import time
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote, unquote
from functools import lru_cache
from os import path

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.GDT_RawResponse import GDT_RawResponse
from gdo.base.Util import hdr, Files, msg, module_config_value, module_enabled, Strings
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Bool import GDT_Bool
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.message.GDT_HTML import GDT_HTML

MARKDOWN_PREVIEW_STYLE = '''
:root { color-scheme: light dark; font-family: system-ui, sans-serif; }
body { max-width: 54rem; margin: 3rem auto; padding: 0 1.5rem 4rem;
       line-height: 1.7; overflow-wrap: break-word; }
h1, h2, h3 { line-height: 1.25; margin-top: 1.8em; }
h1 { font-size: 2.2rem; border-bottom: 2px solid #568c79; padding-bottom: .35em; }
h2 { border-bottom: 1px solid #8886; padding-bottom: .3em; }
a { color: #18775c; text-underline-offset: .18em; }
pre, code { font-family: ui-monospace, monospace; background: #8882; border-radius: .3rem; }
code { padding: .12em .3em; }
pre { padding: 1rem; overflow-x: auto; }
pre code { padding: 0; background: transparent; }
blockquote { border-left: .25rem solid #568c79; margin-left: 0; padding-left: 1rem; color: #777; }
img { max-width: 100%; height: auto; }
table { border-collapse: collapse; display: block; overflow-x: auto; }
th, td { border: 1px solid #8886; padding: .4rem .7rem; }
@media (prefers-color-scheme: dark) { a { color: #7cdbb4; } blockquote { color: #bbb; } }
'''


class MarkdownMetadata(HTMLParser):
    """Extract plain text from the first heading and paragraph of rendered Markdown."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.description = None
        self._tag = None
        self._parts = []
        self._ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self._ignored += 1
        elif not self._ignored and self._tag is None:
            if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self.title is None:
                self._tag, self._parts = tag, []
            elif tag == 'p' and self.description is None:
                self._tag, self._parts = tag, []

    def handle_data(self, data):
        if self._tag and not self._ignored:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self._ignored:
            self._ignored -= 1
        elif tag == self._tag:
            value = ' '.join(''.join(self._parts).split())
            if tag == 'p':
                self.description = value
            else:
                self.title = value
            self._tag = None


class file_server(Method):

    def explicitly_allowed(self, explicitly_allowed: bool = True):
        self._explicitly_allowed = explicitly_allowed
        return self


    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_String('_url').not_null(),
            GDT_Bool('render_md').initial('0'),
        ]

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def get_url(self) -> str:
        return self.param_val('_url').lstrip('/')

    def get_path(self):
        if seo_file := self.get_seo_file():
            return seo_file.get_file().get_path()
        return Application.file_path(self.get_url())

    def get_seo_file(self):
        if not module_enabled('file'):
            return None
        from gdo.file.GDO_SeoFile import GDO_SeoFile
        url = self.get_url()
        return GDO_SeoFile.get_by_url(url if url.isascii() else quote(url, safe='/%'))

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
        # Configuration and secret files must not be exposed as static files.
        if 'secret' in url.lower() or url.lower().endswith('.toml'):
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
        # A public SEO or explicitly allowed file route must not bypass this
        # path rule; challenge secrets are never served by these routes.
        if 'secret' in unquote(self.get_url()).lower():
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        if not self.get_seo_file() and not hasattr(self, '_explicitly_allowed') and file_server.is_forbidden(self.get_url()):
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        file_path = self.get_path()
        if not os.path.isfile(file_path):
            Application.status('404 Not Found')
            return self.err('err_file_not_found')
        if (self.param_val('render_md') == '1' and self.get_url().lower().endswith('.md')
                and module_enabled('markdown')):
            from gdo.markdown.MDConvert import MDConvert
            with open(file_path, encoding='utf-8', errors='replace') as source:
                text = source.read()
                rendered = MDConvert(text).to_html(text)
            metadata = MarkdownMetadata()
            metadata.feed(rendered)
            title = f'<title>{escape(metadata.title)}</title>' if metadata.title else ''
            description = (f'<meta name="description" content="{escape(metadata.description, quote=True)}">'
                           if metadata.description else '')
            image = ''
            root = os.path.realpath(Application.file_path())
            absolute = os.path.abspath(file_path)
            real = os.path.realpath(file_path)
            if (module_enabled('link_preview') and not self.get_seo_file()
                    and not file_server.is_forbidden(self.get_url())
                    and absolute == real and os.path.commonpath((root, real)) == root):
                from gdo.link_preview.MarkdownPreview import MarkdownPreview
                if image_url := MarkdownPreview.for_html(rendered, MARKDOWN_PREVIEW_STYLE):
                    image = f'<meta property="og:image" content="{escape(image_url, quote=True)}">'
            Application.header('X-Content-Type-Options', 'nosniff')
            body = ('<!doctype html><html><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width, initial-scale=1">'
                    + title + description + image + '<style>' + MARKDOWN_PREVIEW_STYLE + '</style></head><body>'
                    + rendered + '</body></html>').encode('utf-8')
            return GDT_RawResponse(body, 'text/html; charset=UTF-8')
        if self.check_etag(file_path):
            Application.status("304 Not Modified")
            return self.empty()
        mime_type = Files.mime(file_path)
        Application.header('Content-Type', mime_type or 'application/octet-stream')
        Application.header('Content-Length', str(path.getsize(file_path)))
        return GDT_FileOut().path(file_path)
