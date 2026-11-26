import unittest
from unittest.mock import MagicMock, patch

from gdo.account.method.set_cli import set_cli
from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.date.GDT_Date import GDT_Date


class SetCliResolutionTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_empty_set_lists_settings(self):
        method = MagicMock()
        method.param_value.return_value = None
        with patch('gdo.account.method.list_cli.list_cli.gdo_execute', return_value='settings') as listing:
            self.assertEqual('settings', set_cli.gdo_execute(method))
        listing.assert_called_once_with(method)
        method._env_user.save_setting.assert_not_called()

    def test_setting_name_is_optional(self):
        with patch.object(GDT_UserSetting, 'KNOWN', {'language': GDT_String('language')}):
            name = set_cli().gdo_parameters()[0]
            self.assertFalse(name.is_not_null())
            self.assertTrue(name.validate(None))

    def test_standalone_settings_is_hidden(self):
        from gdo.account.method.list_cli import list_cli
        self.assertTrue(list_cli().gdo_method_hidden())

    def test_unique_prefix_resolves_to_canonical_setting(self):
        language = GDT_String('language')
        with patch.object(GDT_UserSetting, 'KNOWN', {'language': language}):
            selector = GDT_UserSetting('name').not_null()
            self.assertTrue(selector.validate('lang'))
            self.assertIs(selector.get_value(), language)

    def test_ambiguous_and_unknown_names_do_not_resolve(self):
        choices = {key: GDT_String(key) for key in ('language', 'language_other')}
        with patch.object(GDT_UserSetting, 'KNOWN', choices):
            self.assertFalse(GDT_UserSetting('name').not_null().validate('lang'))
            self.assertFalse(GDT_UserSetting('name').not_null().validate('missing'))
            self.assertIs(GDT_UserSetting('name').not_null().to_value('language'), choices['language'])

    def test_set_uses_resolved_name_for_lookup_and_save(self):
        method = MagicMock()
        method.param_value.return_value = GDT_String('language')
        method.param_val.return_value = 'de'
        setting = MagicMock()
        setting.is_writable.return_value = True
        with patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=setting) as lookup:
            set_cli.gdo_execute(method)
        lookup.assert_called_once_with('language', method._env_user)
        method._env_user.save_setting.assert_called_once_with('language', 'de')

    def test_read_uses_resolved_name_for_lookup(self):
        method = MagicMock()
        method.param_value.return_value = GDT_String('language')
        method.param_val.return_value = None
        setting = MagicMock()
        setting.has_tooltip.return_value = False
        with patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=setting) as lookup:
            set_cli.gdo_execute(method)
        lookup.assert_called_once_with('language', method._env_user)
        method._env_user.save_setting.assert_not_called()

    def test_invalid_date_is_not_saved(self):
        method = MagicMock()
        method.param_value.return_value = GDT_String('birthday')
        method.param_val.return_value = '31.02.1900'
        with patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=GDT_Date('birthday')):
            set_cli.gdo_execute(method)
        method._env_user.save_setting.assert_not_called()
        method.err.assert_called_once_with('err_cli_invalid_date')

    def test_valid_date_is_saved(self):
        method = MagicMock()
        method.param_value.return_value = GDT_String('birthday')
        method.param_val.return_value = '2000-02-29'
        setting = GDT_Date('birthday')
        with patch.object(setting, 'render_val', return_value='none'), \
                patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=setting):
            set_cli.gdo_execute(method)
        method._env_user.save_setting.assert_called_once_with('birthday', '2000-02-29')

    def test_invalid_select_value_is_not_saved(self):
        method = MagicMock()
        method.param_value.return_value = GDT_String('language')
        method.param_val.return_value = 'Deutsch Englisch'
        setting = GDT_UserSetting('test').choices({'en': 'en', 'de': 'de'})
        with patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=setting):
            set_cli.gdo_execute(method)
        method._env_user.save_setting.assert_not_called()
        method.err.assert_called_once()

    def test_select_value_is_saved_as_canonical_key(self):
        method = MagicMock()
        method.param_value.return_value = GDT_String('choice')
        method.param_val.return_value = 'germ'
        setting = GDT_UserSetting('test').choices({'de': 'german', 'en': 'english'})
        with patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=setting):
            set_cli.gdo_execute(method)
        method._env_user.save_setting.assert_called_once_with('choice', 'de')
