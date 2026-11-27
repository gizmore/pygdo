from unittest.mock import MagicMock, patch

from gdo.account.method.set_cli import set_cli
from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.language.GDT_Language import GDT_Language
from gdotest.TestUtil import GDOTestCase


class SetObjectValueTest(GDOTestCase):
    def setUp(self):
        Cache.init()
        Application.mode(Mode.render_cli)
        self.method = MagicMock()
        self.method.param_value.return_value = GDT_String('language')
        self.method._env_mode = Mode.render_cli
        self.method._env_user.get_setting_val.return_value = 'ar'
        self.field = GDT_Language('language').not_null().val('en')
        english, arabic = MagicMock(), MagicMock()
        english.get_id.return_value = 'en'
        arabic.get_id.return_value = 'ar'
        self.resolve = {'en': english, 'ar': arabic}.get

    def test_submitted_object_is_saved_instead_of_previous_value(self):
        self.method.param_val.return_value = 'ar'
        with patch.object(self.field, 'to_value', side_effect=self.resolve), \
                patch.object(self.field, 'render_val', return_value='English'), \
                patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=self.field):
            set_cli.gdo_execute(self.method)
        self.method._env_user.save_setting.assert_called_once_with('language', 'ar')
        self.assertEqual('ar', self.field.get_val())

    def test_invalid_object_is_not_saved_and_original_value_restored(self):
        self.method.param_val.return_value = 'zz'
        with patch.object(self.field, 'to_value', side_effect=self.resolve), \
                patch.object(self.field, 'render_val', return_value='English'), \
                patch.object(self.field, 'render_suggestion', return_value=''), \
                patch.object(self.field, 'render_error', return_value='invalid'), \
                patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=self.field):
            set_cli.gdo_execute(self.method)
        self.method._env_user.save_setting.assert_not_called()
        self.assertEqual('en', self.field.get_val())
        self.method.err.assert_called_once()

    def test_unknown_value_for_nullable_object_is_still_rejected(self):
        self.field.not_null(False)
        self.method.param_val.return_value = 'zz'
        with patch.object(self.field, 'to_value', side_effect=self.resolve), \
                patch.object(self.field, 'render_val', return_value='English'), \
                patch.object(self.field, 'render_error', return_value='invalid'), \
                patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=self.field):
            set_cli.gdo_execute(self.method)
        self.method._env_user.save_setting.assert_not_called()
        self.assertEqual('en', self.field.get_val())
        self.method.err.assert_called_once()
