import sys
import datetime
from contextvars import ContextVar

import aiofiles
from rich.console import Console
from rich.traceback import Traceback

from gdo.base.WithPygdo import WithPygdo

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User




class Logger:
    LINES_WRITTEN = 0 #PYPP#DELETE#

    _base: str
    # Log attribution belongs to the current request/connector task.  A global
    # user leaks identity across concurrently handled connector messages.
    USER: ContextVar = ContextVar('logger_user', default=None)

    @classmethod
    def init(cls, base: str = None):
        cls._base = base
        cls.user(None)
        WithPygdo.util('Files').create_dir(cls._base)

    @classmethod
    def user(cls, user: 'GDO_User'):
        cls.USER.set(user)

    @classmethod
    def get_user(cls) -> 'GDO_User|None':
        return cls.USER.get()

    @classmethod
    def request(cls, url: str, qs: str):
        content = f"{WithPygdo.application().get_request_method()} - {url}{qs}"
        cls.write('message.log', content)

    @classmethod
    async def arequest(cls, url: str, qs: str):
        content = f"{WithPygdo.application().get_request_method()} - {url}{qs}"
        await cls.awrite('message.log', content)

    @classmethod
    def debug(cls, content: str):
        WithPygdo.util('gdo_print')(content)
        cls.write('debug.log', content, False)

    @classmethod
    def error(cls, content: str):
        cls.write('message.log', content)

    @classmethod
    def message(cls, content: str):
        cls.write('message.log', content)

    @classmethod
    def cron(cls, content: str):
        WithPygdo.util('gdo_print')(content)
        cls.write('cron.log', content)

    @classmethod
    def exception(cls, ex: Exception, msg: str = None):
        stack = cls.traceback(ex)
        if msg:
            sys.stderr.write(msg + "\n")
        sys.stderr.write(str(ex)+"\n")
        sys.stderr.write(stack + "\n")
        cls.write('exception.log', str(ex), False)
        cls.write('exception.log', stack, False)

    @classmethod
    def write(cls, path: str, content: str, user_log: bool = True):
        pre = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
        path = datetime.datetime.now().strftime('%Y-%m-%d') + '_' + path
        user = cls.get_user()
        if user:
            pre += user.get_name() + " - "
        with open(f"{cls._base}{path}", 'a', encoding='utf8') as fo:
            fo.write(f'{pre}{content}\n')
            cls.LINES_WRITTEN += 1 #PYPP#DELETE#
        if user and user_log:
            dir_name = f"{cls._base}{user.get_server().get_name()}/{user.get_name()}/"
            WithPygdo.util('Files').create_dir(dir_name)
            with open(f"{dir_name}{path}", 'a', encoding='utf8') as fo:
                fo.write(f'{pre}{content}\n')
            cls.LINES_WRITTEN += 1 #PYPP#DELETE#

    @classmethod
    async def awrite(cls, path: str, content: str, user_log: bool = True):
        pre = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
        path = datetime.datetime.now().strftime('%Y-%m-%d') + '_' + path
        user = cls.get_user()
        if user:
            pre += user.get_name() + " - "
        async with aiofiles.open(f"{cls._base}{path}", 'a', encoding='utf8') as fo:
            await fo.write(f"{pre}{content}\n")
            cls.LINES_WRITTEN += 1  #PYPP#DELETE#
        if user and user_log:
            dir_name = f"{cls._base}{user.get_server().get_name()}/{user.get_name()}/"
            await WithPygdo.util('Files').acreate_dir(dir_name)
            async with aiofiles.open(f"{dir_name}{path}", 'a', encoding='utf8') as fo:
                await fo.write(f"{pre}{content}\n")
                cls.LINES_WRITTEN += 1  #PYPP#DELETE#

    @classmethod
    def traceback(cls, ex) -> str:
        tb = Traceback.from_exception(type(ex), ex, ex.__traceback__, show_locals=True)
        c = Console(record=True, width=120)
        c.print(tb)
        return c.export_text()
