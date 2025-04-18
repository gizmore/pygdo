import os
import signal

import aiofiles

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Util import Files
from gdo.core.GDO_Event import GDO_Event
from gdo.date.Time import Time


class IPC:

    COUNT: int = 0 #PYPP#DELETE#
    PID: int = 0

    #######
    # CLI #
    #######
    @classmethod
    def cli_check_for_ipc(cls):
        from gdo.base.Application import Application
        from gdo.base.Cache import Cache
        ts = Cache.get('ipc', 'ts', Application.TIME) # Trigger IPC events for web via redis timestamp.
        if Application.IPC_TS < ts:
            for event in GDO_Event.query_for_sink('to_cli', ts).exec():
                event.execute_cli()
            Application.IPC_TS = ts
            cut = Time.get_date(ts)
            GDO_Event.table().delete_query().where(f"event_type='to_cli' AND event_created <={cut}")

    #######
    # Dog #
    #######
    @classmethod
    def dog_execute_events(cls):
        ts = Application.TIME
        for event in GDO_Event.query_for_sink('to_dog', ts).exec():
            event.execute_dog()
        cut = Time.get_date(ts)
        GDO_Event.table().delete_query().where(f"event_type='to_dog' AND event_created <={cut}")

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
        now = Application.TIME
        path = Application.file_path('bin/web.pids')
        content = ''
        if os.path.isfile(path):
            async with aiofiles.open(path) as f:
                content = await f.read()
            if pid in content:
                return
        lines = content.strip().split('\n') if content else []
        lines.append(f'{pid}:{now}')
        async with aiofiles.open(path, 'w') as f:
            await f.write('\n'.join(lines) + '\n')



    @classmethod
    def web_check_for_ipc(cls):
        ts = Cache.get('ipc', 'ts', Application.TIME) # Trigger IPC events for web via redis timestamp.
        if Application.IPC_TS < ts:
            for event in GDO_Event.query_for_sink('to_web', ts).exec():
                event.execute_web()
            Application.IPC_TS = ts
        pass


    @classmethod
    def web_cleanup_time(cls):
        path = Application.file_path('bin/web.pids')
        n_proc = int(Application.config('core.processes', '1'))
        # TODO: if more than 8/n lines, keep latest 8, ... always return min ts from <= 8/n lines

    #################
    # Event Sending #
    #################

    @classmethod
    def send(cls, event: str, args: any):
        cls.COUNT += 1 # PYPP#DELETE#
        if Application.IS_HTTP:
            cls.send_to_dog(event, args)
        else:
            cls.send_to_web(event, args)

    @classmethod
    def send_to_dog(cls, event: str, args: any):
        GDO_Event.to_dog(event, args)
        if not cls.PID:
            from gdo.core.method.launch import launch
            cls.PID = int(Files.get_contents(launch.lock_path()))
        try:
            os.kill(cls.PID, signal.SIGUSR1)
        except ProcessLookupError:
            pass

    @classmethod
    def send_to_web(cls, event: str, args: any):
        GDO_Event.to_cli(event, args) # bash is like a web server 1
        GDO_Event.to_web(event, args) # send to web server
        Cache.set('ipc', 'ts', Application.TIME) # Trigger IPC events for web via redis timestamp.
