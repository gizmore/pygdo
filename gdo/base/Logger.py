import asyncio
import datetime
import sys

from typing import TYPE_CHECKING

import aiofiles
import better_exceptions

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User

from gdo.base.Util import Files


class Logger:
    LINES_WRITTEN = 0 #PYPP#DELETE#

    _base: str
    _user: 'GDO_User' = None

    @classmethod
    def init(cls, base: str = None):
        if base:
            cls._base = base
        else:
            from gdo.base.Application import Application
            cls._base = Application.file_path('protected/logs/')
        cls._user = None
        Files.create_dir(cls._base)

    @classmethod
    def user(cls, user: 'GDO_User'):
        cls._user = user

    @classmethod
    def request(cls, url: str, qs: str):
        from gdo.base.Application import Application
        content = f"{Application.get_request_method()} - {url}{qs}"
        cls.write('message.log', content)

    @classmethod
    async def arequest(cls, url: str, qs: str):
        from gdo.base.Application import Application
        content = f"{Application.get_request_method()} - {url}{qs}"
        await cls.awrite('message.log', content)

    @classmethod
    def debug(cls, content: str):
        print(content)
        cls.write('debug.log', content, False)

    @classmethod
    def error(cls, content: str):
        # print(content)
        cls.write('message.log', content)

    @classmethod
    def message(cls, content: str):
#        print(content)
        cls.write('message.log', content)

    @classmethod
    def cron(cls, content: str):
        print(content)
        cls.write('cron.log', content)

    @classmethod
    def exception(cls, ex: Exception):
        stack = "".join(better_exceptions.format_exception(*sys.exc_info()))
        sys.stderr.write(str(ex)+"\n")
        sys.stderr.write(stack + "\n")
        cls.write('exception.log', str(ex), False)
        cls.write('exception.log', stack, False)

    @classmethod
    def write(cls, path: str, content: str, user_log: bool = True):
        pre = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
        if cls._user:
            pre += cls._user.get_name() + " - "
        with open(f"{cls._base}{path}", 'a', encoding='utf8') as fo:
            fo.write(f'{pre}{content}\n')
            cls.LINES_WRITTEN += 1 #PYPP#DELETE#
        if cls._user and user_log:
            dir_name = f"{cls._base}{cls._user.get_server_id()}/{cls._user.get_name()}/"
            Files.create_dir(dir_name)
            with open(f"{dir_name}{path}", 'a', encoding='utf8') as fo:
                fo.write(f'{pre}{content}\n')
            cls.LINES_WRITTEN += 1 #PYPP#DELETE#

    @classmethod
    async def awrite(cls, path: str, content: str, user_log: bool = True):
        pre = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
        if cls._user:
            pre += cls._user.get_name() + " - "
        async with aiofiles.open(f"{cls._base}{path}", 'a', encoding='utf8') as fo:
            await fo.write(f"{pre}{content}\n")
            cls.LINES_WRITTEN += 1  #PYPP#DELETE#
        if cls._user and user_log:
            dir_name = f"{cls._base}{cls._user.get_server_id()}/{cls._user.get_name()}/"
            await Files.acreate_dir(dir_name)
            async with aiofiles.open(f"{dir_name}{path}", 'a', encoding='utf8') as fo:
                await fo.write(f"{pre}{content}\n")
                cls.LINES_WRITTEN += 1  #PYPP#DELETE#
