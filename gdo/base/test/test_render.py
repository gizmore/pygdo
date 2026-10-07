import unittest

from gdo.base.Render import Mode, Render
from gdo.base.Message import Message
from gdo.core.Connector import Connector


class RenderTest(unittest.TestCase):

    def test_plain_text_is_escaped_for_telegram(self):
        self.assertEqual(
            'Answer: &lt;answer&gt;',
            Render.convert_text('Answer: <answer>', Mode.render_txt, Mode.render_telegram),
        )

    def test_html_emphasis_crosses_to_irc(self):
        self.assertEqual(
            '\x02strong\x02 and \x1ditalic\x1d',
            Render.convert_text('<b>strong</b> and <i>italic</i>', Mode.render_html, Mode.render_irc),
        )

    def test_irc_emphasis_crosses_to_telegram(self):
        self.assertEqual(
            '<b>strong</b> &lt;literal&gt;',
            Render.convert_text('\x02strong\x02 <literal>', Mode.render_irc, Mode.render_telegram),
        )

    def test_irc_to_gdt_keeps_irc_emphasis_before_editor_serialization(self):
        tree = Render.irc_to_gdt('\x02strong\x02')
        self.assertEqual('<b>strong</b>', tree.render(Mode.render_telegram))

    def test_unknown_html_is_reduced_to_its_safe_text_content(self):
        self.assertEqual(
            'ok',
            Render.convert_text('<answer>ok</answer>', Mode.render_html, Mode.render_telegram),
        )

    def test_connector_converts_plain_result_immediately_before_delivery(self):
        class TelegramConnector(Connector):
            def get_render_mode(self):
                return Mode.render_telegram

        message = Message('', Mode.render_irc).result('Answer: <answer>')
        TelegramConnector().render_outgoing(message)
        self.assertEqual('Answer: &lt;answer&gt;', message._result)
        self.assertEqual(Mode.render_telegram, message._result_mode)
