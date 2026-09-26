from unittest.mock import AsyncMock, MagicMock

from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdotest.TestUtil import GDOTestCase


class PrivateReplyTest(GDOTestCase):

    async def test_private_notice_bypasses_source_channel(self):
        connector = MagicMock()
        connector.send_to_channel = AsyncMock()
        connector.send_to_user = AsyncMock()
        server = MagicMock()
        server.get_connector.return_value = connector
        user = MagicMock()
        message = Message('$help', Mode.render_irc)
        message.env_server(server).env_channel(MagicMock())
        # Avoid creating a database-backed session; delivery only needs a reply target.
        message._env_user = user
        message._env_reply_to = user
        message.result('Commands: ...').reply_privately(notice=True)

        await message.deliver()

        connector.send_to_channel.assert_not_called()
        connector.send_to_user.assert_awaited_once_with(message, True, True)
