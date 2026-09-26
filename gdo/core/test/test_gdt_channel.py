import os.path
from unittest.mock import MagicMock

from gdotest.TestUtil import GDOTestCase

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.GDT_Channel import GDT_Channel


class GDTChannelTest(GDOTestCase):

    async def asyncSetUp(self):
        Application.IS_TEST = True
        Application.init(os.path.dirname(__file__) + '/../../..')
        await super().asyncSetUp()

    def test_default_current_resolves_message_channel_without_input(self):
        channel = MagicMock()
        Message('', Mode.render_cli).env_channel(channel)

        self.assertIs(channel, GDT_Channel('channel').default_current().get_value())
