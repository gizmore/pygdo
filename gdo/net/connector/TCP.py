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


class TcpGhostSession:
    """Transient per-socket state before TCP authentication.

    Ghost is deliberately not a database user, so it cannot own a persisted
    ``GDO_Session`` either.
    """

    def __init__(self):
        self._data = {}

    def get(self, key: str, default: Any = None):
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        return self

    def remove(self, key: str):
        self._data.pop(key, None)
        return self

    def save(self):
        return self


class TcpSession:
    def __init__(self, reader, writer, connector, user):
        self.reader = reader
        self.writer = writer
        self.connector = connector
        self.user = user
        self.channel = self.connector._server.get_or_create_channel(self.user.get_name())
        self.session = TcpGhostSession() if user.is_ghost() else GDO_Session.for_user(user)

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
                msg.env_user(self.user).env_server(self.connector._server).env_channel(self.channel).env_mode(Mode.render_cli).env_session(self.session)
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
            await self.connector.close_session(self)


class TCP(Connector):

    _sessions: dict[int,TcpSession]

    _socket: Any

    def render_user_connect_help(self) -> str:
        from gdo.net.module_net import module_net
        m = module_net.instance()
        ip = socket.gethostbyname(Application.config('core.domain'))
        return f'netcat {ip} {m.cfg_port()}'

    async def gdo_connect(self) -> bool:
        from gdo.net.module_net import module_net
        m = module_net.instance()
        Logger.debug(f'Waiting for TCP connections on {m.cfg_host()}:{m.cfg_port()}')
        self._sessions = {}
        asyncio.create_task(self.mainloop())
        self._connected = True
        return True

    async def mainloop(self):
        from gdo.net.module_net import module_net
        m = module_net.instance()
        self._socket = await asyncio.start_server(self._accept_client, m.cfg_host(), m.cfg_port())

    async def _accept_client(self, reader, writer):
        # A TCP peer is anonymous until tcpauth succeeds. Do not leave a
        # database user behind merely because somebody opened a socket.
        session = TcpSession(reader, writer, self, GDO_User.ghost())
        self._sessions[id(session)] = session
        asyncio.create_task(session.run())

    async def authenticate_session(self, session: TcpSession, user: GDO_User) -> bool:
        """Turn an anonymous TCP connection into an authenticated user session."""
        old_user = session.user
        old_uid = old_user.get_id()
        user_uid = user.get_id()
        other = self.session_for_user(user)
        if other is not None and other is not session:
            return False
        if old_uid == user_uid:
            return True

        if old_user.get_name() in self._server._users:
            await self._server.on_user_quit(old_user)
        if user.get_name() not in self._server._users:
            await self._server.on_user_joined(user)

        session.user = user
        session.session = GDO_Session.for_user(user)
        session.channel = self._server.get_or_create_channel(user.get_name(), creator=user)
        await user.authenticate(session.session)
        return True

    def session_for_user(self, user: GDO_User) -> TcpSession | None:
        for session in self._sessions.values():
            if session.user.get_id() == user.get_id():
                return session
        return None

    async def authenticate_user(self, old_user: GDO_User, user: GDO_User, gdo_session: GDO_Session = None) -> bool:
        if gdo_session is not None:
            for session in self._sessions.values():
                if session.session is gdo_session:
                    return await self.authenticate_session(session, user)
            return False
        session = self.session_for_user(old_user)
        return session is not None and await self.authenticate_session(session, user)

    async def close_session(self, session: TcpSession):
        """Remove only the disconnected client, never the shared TCP listener."""
        if self._sessions.get(id(session)) is not session:
            return
        del self._sessions[id(session)]
        user = session.user
        if not user.is_ghost() and user.get_name() in self._server._users:
            await self._server.on_user_quit(user)

    async def send_to_user(self, msg: Message, with_events: bool=True, notice: bool=False):
        uid = msg._env_user.get_id()
        if session := self.session_for_user(msg._env_user):
            await session.send(f"#- {msg._env_user.render_name}{{{self._server.render_name()}}}  {msg._result}")
        else:
            Logger.error(f"Cannot deliver TCP message to offline user {uid}")

    async def send_to_channel(self, msg: Message, with_events: bool=True):
        channel = msg._env_channel
        chan_name = "#" + channel.get_name() if not channel.get_name().startswith("#") else channel.get_name()
        user = self._server.get_user_by_name(channel.get_name())
        if user and (session := self.session_for_user(user)):
            await session.send(f"{chan_name} {msg._env_user.render_name}{{{self._server.render_name()}}}  {msg._result}")
        else:
            Logger.error(f"Cannot deliver TCP channel message to {channel.get_name()}")
