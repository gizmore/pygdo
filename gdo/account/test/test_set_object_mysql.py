import os
import unittest
from unittest.mock import MagicMock, patch

from gdo.account.method.set_cli import set_cli
from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.language.GDO_Language import GDO_Language
from gdo.language.GDT_Language import GDT_Language
from gdotest.TestUtil import GDOTestCase


@unittest.skipUnless(os.environ.get('SET_MYSQL_TEMP_TEST') == '1', 'requires isolated MySQL test config')
class SetObjectMySQLTest(GDOTestCase):
    def test_language_setting_uses_submitted_iso(self):
        Application.init_test(os.getcwd())
        self.assertEqual('pygdo_test', Application.config('db.name'))
        Application.mode(Mode.render_cli)
        db = Application.db()
        original = db.query
        with patch.object(db, 'query', side_effect=lambda query, *args, **kwargs:
                          original(query.replace('CREATE TABLE IF NOT EXISTS ',
                                                 'CREATE TEMPORARY TABLE ', 1), *args, **kwargs)):
            db.create_table(GDO_Language.table())
        for iso, name in [('en', 'English'), ('ar', 'Arabic')]:
            GDO_Language.blank({'lang_iso': iso, 'lang_english': name, 'lang_native': name,
                                'lang_supported': '1'}).insert()
        field = GDT_Language('language').not_null().val('en')
        method = MagicMock()
        method._env_mode = Mode.render_cli
        method.param_value.return_value = GDT_String('language')
        method.param_val.return_value = 'ar'
        method._env_user.get_setting_val.return_value = 'ar'
        with patch('gdo.account.method.set_cli.GDO_UserSetting.setting_column', return_value=field):
            set_cli.gdo_execute(method)
        method._env_user.save_setting.assert_called_once_with('language', 'ar')
