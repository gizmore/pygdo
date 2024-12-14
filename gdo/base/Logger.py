import traceback
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User

from gdo.base.Util import Files


class Logger:
    _base: str
    _user: 'GDO_User'

    @classmethod
    def init(cls):
        from gdo.base.Application import Application
        cls._base = Application.file_path('protected/logs/')
        Files.create_dir(cls._base)
        cls._user = None

    @classmethod
    def uid(cls, uid: str):
        cls._uid = uid

    @classmethod
    def debug(cls, content: str):
        print(content)
        cls.write('debug.log', content)

    @classmethod
    def error(cls, content: str):
        print(content)
        cls.write('error.log', content)

    @classmethod
    def message(cls, content: str):
        print(content)
        cls.write('message.log', content)

    @classmethod
    def exception(cls, ex: Exception):
        sys.stderr.write(str(ex)+"\n")
        sys.stderr.write(traceback.format_exc() + "\n")
        cls.write('exception.log', str(ex))
        cls.write('exception.log', traceback.format_exc())

    @classmethod
    def write(cls, path: str, content: str):
        with open(f"{cls._base}{path}", 'a') as fo:
            fo.write(f'{content}\n')
        if cls._user:
            dir_name = f"{cls._base}{cls._user.get_server().get_name()}/{cls._user.get_name()}/"
            Files.create_dir(dir_name)
            with open(f"{dir_name}{path}", 'a') as fo:
                fo.write(f'{content}\n')
