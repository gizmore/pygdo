import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Render import Mode
from gdo.core.GDT_Template import Templite
from gdo.mira_remember.GDT_Stance import GDT_Stance
from gdo.ui.GDT_IconedEnum import GDT_IconedEnum


class IconedEnumTest(unittest.TestCase):
    def test_stance_defaults_and_icons_follow_value(self):
        field = GDT_Stance()
        self.assertEqual('neutral', field.get_val())
        with patch('gdo.ui.GDT_IconedEnum.IconProvider.display_icon', side_effect=lambda name, mode: name):
            self.assertEqual('legal', field.render_icon(Mode.render_html))
            field.val('aggressive')
            self.assertEqual('flash', field.render_icon(Mode.render_html))
            field.val('passive')
            self.assertEqual('pause', field.render_icon(Mode.render_html))

    def test_generic_form_encodes_choice_icon_html(self):
        field = GDT_IconedEnum('example').choices({'a': 'A', 'b': 'B'}).icons({'a': 'flash', 'b': 'pause'}).val('a')
        with patch('gdo.ui.GDT_IconedEnum.IconProvider.display_icon', return_value='<i class="x"></i>'), \
             patch.object(field, 'render_label', return_value='Example'):
            rendered = Templite('gdo/ui/tpl/form_iconed_enum.html', caching=False).render(field=field)
        self.assertIn('data-iconed-enum', rendered)
        self.assertIn('data-icon-html="&lt;i class=&quot;x&quot;&gt;&lt;/i&gt;"', rendered)
        self.assertIn('<span data-iconed-enum-icon><i class="x"></i></span>', rendered)

    def test_form_registers_ui_script_when_started_from_cli(self):
        field = GDT_IconedEnum('example').choices({'a': 'A'}).icons({'a': 'flash'}).val('a')
        ui = MagicMock()
        ui.www_path.return_value = '/gdo/ui/js/pygdo-ui.js'
        ui.gdt_page.return_value._js = []
        with patch('gdo.ui.GDT_IconedEnum.Application.IS_HTTP', True), \
             patch('gdo.ui.module_ui.module_ui.instance', return_value=ui), \
             patch('gdo.ui.GDT_IconedEnum.tpl', return_value='form'):
            self.assertEqual('form', field.render_form())
        ui.add_js.assert_called_once_with('js/pygdo-ui.js')
