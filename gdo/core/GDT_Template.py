import os
import re
import sys
import traceback

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.base.Util import html, Files, dump
from gdo.date.Time import Time


class Templite(object):
    cache = {}
    delimiters = ('<%', '%>')

    def __init__(self, text=None, filename=None, encoding='utf-8', delimiters=None, caching=True):
        """Loads a template from string or file."""
        if filename:
            filename = os.path.abspath(filename)
            mtime = os.path.getmtime(filename)
            self.file = key = filename
        elif text is not None:
            self.file = mtime = None
            key = hash(text)
        else:
            raise ValueError('either text or filename required')
        # set attributes
        self.encoding = encoding
        self.caching = caching
        if delimiters:
            start, end = delimiters
            if len(start) != 2 or len(end) != 2:
                raise ValueError('each delimiter must be two characters long')
            self.delimiters = delimiters
        cache = self.cache
        if caching and key in cache and cache[key][0] == mtime:
            self._code = cache[key][1]
            return
        # read file
        if filename:
            with open(filename) as fh:
                text = fh.read()
        self._code = self._compile(text)
        if caching:
            cache[key] = (mtime, self._code)

    def _compile(self, source):
        offset = 0
        tokens = ['# -*- coding: %s -*-' % self.encoding]
        start, end = self.delimiters
        escaped = (re.escape(start), re.escape(end))
        regex = re.compile('%s(.*?)%s' % escaped, re.DOTALL)
        for i, part in enumerate(regex.split(source)):
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
        return compile('\n'.join(tokens), self.file or '<string>', 'exec')

    def render(self, **namespace):
        """Renders the template according to the given namespace."""
        stack = []
        namespace['__file__'] = self.file

        # add write method
        def write(*args):
            for value in args:
                stack.append(str(value))

        def writeln(line: str):
            write(f"{line}\n")

        namespace['write'] = write
        namespace['writeln'] = writeln

        # add include method
        def include(file):
            if not os.path.isabs(file):
                if self.file:
                    base = os.path.dirname(self.file)
                else:
                    base = os.path.dirname(sys.argv[0])
                file = os.path.join(base, file)
            t = Templite(None, file, self.encoding,
                         self.delimiters, self.caching)
            stack.append(t.render(**namespace))

        namespace['include'] = include
        namespace['Time'] = Time
        namespace['t'] = t
        namespace['Mode'] = Mode
        namespace['html'] = html

        exec(self._code, namespace)
        return ''.join(stack)


class GDT_Template(GDT):

    THEMES: dict[str, str] = {}

    _t_module: str
    _t_file: str
    _t_vals: dict

    # __slots__ = (
    #     '_t_module',
    #     '_t_file',
    #     '_t_vals',
    # )

    def __init__(self):
        super().__init__()

    def template(self, modulename: str, filename: str, vals: dict = None):
        self._t_module = modulename
        self._t_file = filename
        self._t_vals = vals
        return self

    def render(self, mode: Mode = Mode.HTML):
        return self.python(self._t_module, self._t_file, self._t_vals)

    @classmethod
    def render_template(cls, path: str, vals: dict[str, any]):
        data = {
            "modules": ModuleLoader.instance()._cache,
            "Mode": Mode,
            "Application": Application,
        }
        data.update(vals)
        lite = Templite(None, path)
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
    def get_path(cls, modulename: str, path: str):
        for theme_path in cls.THEMES.values():
            p = f"{theme_path}{modulename}/{path}"
            if Files.is_file(p):
                return p
        return os.path.join(Application.PATH, f"gdo/{modulename}/tpl/{path}")


def tpl(modulename: str, filename: str, vals: dict = None):
    return GDT_Template.python(modulename, filename, vals)
