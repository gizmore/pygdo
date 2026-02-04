import asyncio
import socket
from typing import Any

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.Connector import Connector
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User


class TcpSession:
    def __init__(self, reader, writer, connector, user):
        self.reader = reader
        self.writer = writer
        self.connector = connector
        self.user = user
        self.channel = self.connector._server.get_or_create_channel(self.user.get_name())
        self.session = GDO_Session.for_user(self.user)

    async def send(self, text: str):
        self.writer.write((text + "\r\n").encode("utf-8", "ignore"))
        await self.writer.drain()

    async def run(self):
        try:
            Application.set_current_user(self.user)
            await self.send("HELO")
            while True:
                data = await self.reader.readline()
                if not data: break
                Application.tick()
                Application.fresh_page()
                Application.mode(Mode.render_cli)
                Application.set_current_user(self.user)
                line = data.decode("utf-8", "ignore").rstrip("\r\n")
                if line in ("exit", "quit"): break
                msg = Message(line, Mode.render_cli)
                msg.env_user(self.user).env_server(self.connector._server).env_mode(Mode.render_cli).env_session(self.session)
                try:
                    await msg.execute()
                except Exception as ex:
                    Logger.exception(ex, "TCP Connector mainloop")
        finally:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception as ex:
                Logger.exception(ex, "TCP Connector mainloop")
            self.connector.disconnect("QUIT")


class TCP(Connector):

    _sessions: dict[str,TcpSession]

    _socket: Any

    def render_user_connect_help(self) -> str:
        from gdo.net.module_net import module_net
        m = module_net.instance()
        ip = socket.gethostbyname(Application.config('core.domain'))
        return f'netcat {ip} {m.cfg_port()}'

    async def gdo_connect(self) -> bool:
        self._sessions = {}
        asyncio.create_task(self.mainloop())
        self._connected = True
        return True

    async def mainloop(self):
        from gdo.net.module_net import module_net
        m = module_net.instance()
        self._socket = await asyncio.start_server(self._accept_client, m.cfg_host(), m.cfg_port())

    async def _accept_client(self, reader, writer):
        peer = writer.get_extra_info("peername")
        username = f"tcp_{peer[0]}:{peer[1]}"
        next_uid = GDO_User.table().select('user_id + 1').order('user_id DESC').first().exec().fetch_val()
        user = await self._server.get_or_create_user(f'TCP_{next_uid}')
        user.save_val('user_displayname', username)
        session = TcpSession(reader, writer, self, user)
        self._sessions[user.get_id()] = session
        asyncio.create_task(session.run())

    async def send_to_user(self, msg: Message, with_events: bool=True, notice: bool=False):
        uid = msg._env_user.get_id()
        await self._sessions[uid].send(msg._result)

    async def send_to_channel(self, msg: Message, with_events: bool=True):
        await self.send_to_user(msg, with_events)
