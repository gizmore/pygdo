import functools
import os
import re
from io import StringIO
from typing import Any

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.base.Util import html, Files


class Templite(object):
    cache = {}
    delimiters = ('<%', '%>')
    PATTERN = re.compile('%s(.*?)%s' % delimiters, re.DOTALL)

    def __init__(self, filename: str, encoding: str='utf-8', caching: bool=True):
        filename = os.path.abspath(filename)
        self.file = key = filename
        self.encoding = encoding
        self.caching = caching
        cache = self.cache
        if caching:
            if key in cache:
                self._code = cache[key]
                return
            else:
                pass
        with open(filename) as fh:
            text = fh.read()
        self._code = self._compile(text)
        if caching:
            cache[key] = self._code

    def _compile(self, source):
        offset = 0
        tokens = ['# -*- coding: %s -*-' % self.encoding]
        start, end = self.delimiters
        for i, part in enumerate(self.PATTERN.split(source)):
            part = part.replace('\\'.join(start), start)
            part = part.replace('\\'.join(end), end)
            if i % 2 == 0:
                if not part:
                    continue
                part = part.replace('\\', '\\\\').replace('"', '\\"')
                part = '\t' * offset + 'write("""%s""")' % part
            else:
                part = part.rstrip()
                if not part:
                    continue
                part_stripped = part.lstrip()
                if part_stripped.startswith(':'):
                    if not offset:
                        raise SyntaxError('no block statement to terminate: ${%s}$' % part)
                    offset -= 1
                    part = part_stripped[1:]
                    if not part.endswith(':'): continue
                elif part_stripped.startswith('='):
                    part = 'write(%s)' % part_stripped[1:]
                lines = part.splitlines()
                margin = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
                part = '\n'.join('\t' * offset + l[margin:] for l in lines)
                if part.endswith(':'):
                    offset += 1
            tokens.append(part)
        if offset:
            raise SyntaxError('%i block statement(s) not terminated' % offset)
        return compile('\n'.join(tokens), self.file, 'exec')

    def render(self, **namespace):

        stack = StringIO()
        write = stack.write

        def writeln(line: str):
            stack.write(line)
            stack.write("\n")

        namespace['write'] = write
        namespace['writeln'] = writeln

        def include(module: str, file: str, args: dict[str, Any]):
            return stack.write(GDT_Template().template(module, file, args).render())

        from gdo.ui.GDT_Page import GDT_Page

        namespace['include'] = include
        namespace['GDT_Page'] = GDT_Page
        namespace['t'] = t
        namespace['Mode'] = Mode
        namespace['html'] = html

        exec(self._code, namespace)
        return stack.getvalue()


class GDT_Template(GDT):

    THEMES: dict[str, str] = {}

    _t_module: str
    _t_file: str
    _t_vals: dict

    __slots__ = (
        '_t_module',
        '_t_file',
        '_t_vals',
    )

    def template(self, modulename: str, filename: str, vals: dict = None):
        self._t_module = modulename
        self._t_file = filename
        self._t_vals = vals
        return self

    def render(self, mode: Mode = Mode.render_html):
        return self.render_html()

    def render_html(self, mode: Mode = Mode.render_html):
        return self.python(self._t_module, self._t_file, self._t_vals)

    @classmethod
    def render_template(cls, path: str, vals: dict[str, any]):
        data = {
            # "modules": ModuleLoader.instance()._cache,
            "Mode": Mode,
            "Application": Application,
        }
        data.update(vals)
        lite = Templite(path)
        return lite.render(**data)

    @classmethod
    def python(cls, modulename: str, filename: str, vals: dict[str, any]):
        try:
            path = cls.get_path(modulename, filename)
            return cls.render_template(path, vals)
        except Exception as ex:
            Logger.exception(ex)
            raise ex

    @classmethod
    def register_theme(cls, name: str, path: str):
        cls.THEMES[name] = path

    @classmethod
    @functools.cache
    def get_path(cls, modulename: str, path: str):
        for theme_path in cls.THEMES.values():
            p = f"{theme_path}{modulename}/{path}"
            if Files.is_file(p):
                return p
        return os.path.join(Application.PATH, f"gdo/{modulename}/tpl/{path}")

def tpl(modulename: str, filename: str, vals: dict = None):
    return GDT_Template.python(modulename, filename, vals)
