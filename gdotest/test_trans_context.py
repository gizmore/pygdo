import asyncio
import unittest
from gdotest.TestUtil import GDOTestCase
from unittest.mock import AsyncMock, Mock, patch

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.base.Trans import Trans, t, tiso, tusr


class TranslationContextTest(GDOTestCase):
    def setUp(self):
        Application.mode(Mode.render_txt)
        Application.STORAGE.lang = 'en'
        self.cache = patch.dict(Trans.EN, {'test_trigger': 'Try $t$help, %s, $t$ping'})
        self.cache.start()

    def tearDown(self):
        self.cache.stop()

    def destination(self, prefix):
        obj = Mock()
        obj.get_trigger.return_value = prefix
        return obj

    def test_fallback_and_nested_exception_restore(self):
        self.assertEqual('Try $help, x, $ping', t('test_trigger', ('x',)))
        with Trans.message_context(self.destination('!')):
            with self.assertRaises(ValueError):
                with Trans.message_context(self.destination('!'), self.destination('.')):
                    self.assertEqual('Try .help, x, .ping', Trans.t('test_trigger', ('x',)))
                    raise ValueError()
            self.assertEqual('!', Trans.TRIGGER.get())
        self.assertEqual('$', Trans.TRIGGER.get())

    def test_channel_none_prefix_falls_back_to_server(self):
        with Trans.message_context(self.destination('%'), self.destination(None)):
            self.assertEqual('Try %help, x, %ping', tiso('en', 'test_trigger', ('x',)))
            user = Mock()
            user.get_lang_iso.return_value = 'en'
            self.assertEqual('Try %help, x, %ping', tusr(user, 'test_trigger', ('x',)))

    async def test_simultaneous_messages_keep_their_prefix(self):
        ready = asyncio.Event()
        count = 0
        async def render(prefix):
            nonlocal count
            msg = Message('anything', Mode.render_txt)
            msg._env_server = self.destination('$')
            msg._env_channel = self.destination(prefix)
            async def execute():
                nonlocal count
                count += 1
                if count == 2:
                    ready.set()
                await ready.wait()
                await asyncio.sleep(0)
                return t('test_trigger', ('x',))
            msg._execute_in_context = execute
            return await msg.execute()
        self.assertEqual(['Try !help, x, !ping', 'Try .help, x, .ping'],
                         await asyncio.gather(render('!'), render('.')))
        self.assertEqual('$', Trans.TRIGGER.get())

    async def test_cancelled_message_restores_context(self):
        msg = Message('', Mode.render_txt)
        msg._env_server = self.destination('!')
        msg._execute_in_context = AsyncMock(side_effect=asyncio.CancelledError)
        with self.assertRaises(asyncio.CancelledError):
            await msg.execute()
        self.assertEqual('$', Trans.TRIGGER.get())
