import unittest
from unittest.mock import patch

from gdo.base.Render import Mode
from gdo.base.Application import Application
from gdo.date.GDT_Duration import GDT_Duration


class DurationFormTest(unittest.TestCase):
    def test_card_includes_label_and_formatted_duration(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None):
            duration = GDT_Duration('delay')
        with patch.object(duration, 'render_card_label', return_value='Clock Delay'), \
             patch.object(duration, 'get_value', return_value=16.186), \
             patch('gdo.date.GDT_Duration.Time.human_duration', return_value='16s 186ms'):
            self.assertEqual('<p>Clock Delay: 16s 186ms</p>', duration.render(Mode.render_card))

    def test_countdown_card_keeps_live_countdown_markup(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None), \
             patch.object(Application, 'TIME', 100), \
             patch('gdo.date.GDT_Duration.Time.human_duration', return_value='10s'):
            duration = GDT_Duration('delay').countdown_until(110, '<done>')
            with patch.object(duration, 'render_card_label', return_value='Delay'):
                card = duration.render(Mode.render_card)
        self.assertIn('<p>Delay: <span class="gdt-duration-countdown"', card)
        self.assertIn('data-countdown-ended="&lt;done&gt;"', card)
        self.assertTrue(card.endswith('>10s</span></p>'))

    def test_countdown_renders_escaped_end_state_and_server_fallback(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None), \
             patch.object(Application, 'TIME', 100), \
             patch('gdo.date.GDT_Duration.Time.human_duration', return_value='10s'):
            duration = GDT_Duration('delay').countdown_until(110, '<done>')
            html = duration.render(Mode.render_html)
            self.assertIn('data-countdown-until="110.0"', html)
            self.assertIn('data-countdown-ended="&lt;done&gt;"', html)
            self.assertIn('>10s</span>', html)
            duration.countdown_until(90, '<done>')
            self.assertIn('>&lt;done&gt;</span>', duration.render(Mode.render_html))

    def test_form_mode_renders_editable_string_field(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None):
            duration = GDT_Duration('delay').initial('10s')
        self.assertEqual('clock', duration._icon_name)
        with patch.object(duration, 'render_form', return_value='<input>') as render:
            self.assertEqual('<input>', duration.render(Mode.render_form))
        render.assert_called_once()
