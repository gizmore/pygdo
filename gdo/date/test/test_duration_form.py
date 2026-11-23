import unittest
from unittest.mock import patch

from gdo.base.Render import Mode
from gdo.date.GDT_Duration import GDT_Duration


class DurationFormTest(unittest.TestCase):
    def test_form_mode_renders_editable_string_field(self):
        with patch('gdo.base.Application.Application.get_mode', return_value=None):
            duration = GDT_Duration('delay').initial('10s')
        self.assertEqual('clock', duration._icon_name)
        with patch.object(duration, 'render_form', return_value='<input>') as render:
            self.assertEqual('<input>', duration.render(Mode.render_form))
        render.assert_called_once()
