import asyncio
import os
import signal
from functools import lru_cache
from typing import Any

import aiofiles
import msgspec.json
from redis.exceptions import RedisError

from gdo.base.Application import Application
from gdo.base.AsyncRunner import AsyncRunner
from gdo.base.Cache import Cache
from gdo.base.Logger import Logger
from gdo.base.Util import Files, msg
from gdo.core.GDO_Event import GDO_Event
from gdo.date.Time import Time


class IPC:

    MAX_EVENT_ARG_SIZE = 1024
    COUNT: int = 0 #PYPP#DELETE#
    PID: int = 0
    REDIS_QUEUE = 'ipc:dog:queue'
    DOG_POLL_INTERVAL = 1.0
    DOG_NEXT_CHECK = 0.0

    #######
    # CLI #
    #######
    @classmethod
    def cli_check_for_ipc(cls):
        from gdo.base.Application import Application
        from gdo.base.Cache import Cache
        ts = Cache.get('ipc', 'ts_web', 0) # Trigger IPC events for web via redis timestamp.
        if Application.IPC_TS < ts:
            for event in GDO_Event.query_for_sink('to_cli', ts).exec():
                event.execute_cli()
            Application.IPC_TS = ts
            cut = Time.get_date(ts)
            GDO_Event.table().delete_query().where(f"event_type='to_cli' AND event_created <='{cut}'")

    #######
    # Dog #
    #######
    @classmethod
    async def dog_execute_events(cls):
        ts = Application.TIME
        for event in GDO_Event.query_for_sink('to_dog', ts).exec():
            try:
                await event.execute_dog()
            except Exception as ex:
                Logger.exception(ex, "IPC to_dog failed")
        cut = Time.get_date(ts)
        GDO_Event.table().delete_query().where(f"event_type='to_dog' AND event_created <='{cut}'").exec()

    @classmethod
    async def execute_dog_event(cls, event_name: str, args: Any = None):
        from gdo.base.ModuleLoader import ModuleLoader
        from gdo.core.GDO_User import GDO_User
        from gdo.core.connector.Bash import Bash
        module_name, method_name = event_name.split('.', 1)
        method = ModuleLoader.instance().get_module_method(module_name, method_name)
        if args:
            method._raw_args.add_cli_line(args)
        return await method.env_user(GDO_User.system()).env_server(Bash.get_server()).execute()

    @classmethod
    async def dog_check_for_ipc(cls):
        if cls.cfg_dog_mode() != 'redis' or Application.TIME < cls.DOG_NEXT_CHECK:
            return
        cls.DOG_NEXT_CHECK = Application.TIME + cls.DOG_POLL_INTERVAL
        if not Cache.RCACHE:
            return
        while payload := Cache.RCACHE.lpop(cls.REDIS_QUEUE):
            try:
                event = msgspec.json.decode(payload)
                await cls.execute_dog_event(event['name'], event.get('args'))
            except Exception as ex:
                Logger.exception(ex, 'IPC Redis event failed')

    #######
    # Web #
    ########
    @classmethod
    async def web_register_ipc(cls):
        await cls.web_register_ipc_with(os.getpid())

    @classmethod
    async def web_register_ipc_with(cls, pid: int):
        from gdo.base.Application import Application
        pid = str(pid)
        path = Application.file_path('bin/web.pids')
        content = ''
        if os.path.isfile(path):
            async with aiofiles.open(path) as f:
                content = await f.read()
            if pid in content:
                return
        now = Time.get_date(Application.TIME)
        lines = content.strip().split('\n') if content else []
        lines.append(f'{pid}:{now}')
        async with aiofiles.open(path, 'w') as f:
            await f.write('\n'.join(lines) + '\n')



    @classmethod
    async def web_check_for_ipc(cls):
        ts = Cache.get('ipc', 'ts_web', 0)
        if Application.IPC_TS < ts:
            for event in GDO_Event.query_for_sink('to_web', Application.IPC_TS).exec():
                await event.execute_web()
            Application.IPC_TS = ts


    @classmethod
    def web_cleanup_time(cls) -> float:
        path = Application.file_path('bin/web.pids')
        n_proc = int(Application.config('core.processes', '1'))
        with open(path) as f:
            lines = f.readlines()
            if len(lines) > 8:
                lines = lines[-8:]
            date = lines[0].split(':')[1]
            return Time.parse_time(date)

        # TODO: if more than 8/n lines, keep latest 8, ... always return min ts from <= 8/n lines

    #################
    # Event Sending #
    #################

    @classmethod
    def send(cls, event: str, args: Any = None):
        cls.COUNT += 1 #PYPP#DELETE#
        if Application.is_unit_test():
            coro = GDO_Event.blank({
                'event_type': 'to_dog',
                'event_name': event,
                'event_args': GDO_Event.table().column('event_args').to_val(args),
            }).execute_dog()
            Application.run_coro(coro, 'IPC_DOG')
        elif Application.IS_DOG:
            cls.send_to_web(event, args)
        elif Application.IS_HTTP:
            cls.send_to_dog(event, args)

    @classmethod
    @lru_cache
    def method_launch(cls):
        from gdo.core.method.launch import launch
        return launch

    @classmethod
    def send_to_dog(cls, event: str, args: Any):
        if cls.cfg_dog_mode() == 'redis' and cls.send_to_dog_redis(event, args):
            return
        GDO_Event.to_dog(event, args)
        if not cls.PID:
            cls.PID = int(Files.get_contents(cls.method_launch()().lock_path(), False) or 0)
        try:
            if cls.PID:
                os.kill(cls.PID, signal.SIGUSR1)
        except ProcessLookupError:
            cls.PID = 0

    @classmethod
    def send_to_dog_redis(cls, event: str, args: Any) -> bool:
        if not Cache.RCACHE:
            return False
        try:
            Cache.RCACHE.rpush(cls.REDIS_QUEUE, msgspec.json.encode({'name': event, 'args': args}))
            return True
        except RedisError as ex:
            Logger.exception(ex, 'Cannot enqueue IPC Redis event')
            return False

    @classmethod
    def cfg_dog_mode(cls) -> str:
        from gdo.core.module_core import module_core
        return module_core.instance().cfg_ipc_dog_mode()

    @classmethod
    def send_to_web(cls, event: str, args: Any):
        GDO_Event.to_cli(event, args) # bash is like a web server 1
        GDO_Event.to_web(event, args) # send to web server
        Cache.set('ipc', 'ts_web', Application.TIME) # Trigger IPC events for web via redis timestamp.
