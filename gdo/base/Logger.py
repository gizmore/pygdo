import sys
import traceback

from gdo.base.Util import Files


class Logger:
    _base: str

    @classmethod
    def init(cls):
        from gdo.base.Application import Application
        cls._base = Application.file_path('protected/logs/')
        Files.create_dir(cls._base)

    @classmethod
    def debug(cls, content: str):
        cls.write('debug.log', content)

    @classmethod
    def exception(cls, ex: Exception):
        sys.stderr.write(str(ex))
        sys.stderr.write(traceback.format_exc())

    @classmethod
    def write(cls, path: str, content: str):
        with open(f"{cls._base}{path}", 'a') as fo:
            fo.write(f'{content}\n')
