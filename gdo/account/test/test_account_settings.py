import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import cli_plug, reinstall_module, cli_gizmore, web_plug


class AccountTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()
        reinstall_module('account')
        ModuleLoader.instance().init_cli()
        return self

    def test_01_settings(self):
        result = cli_plug(None, 'settings')
        self.assertIn('language(en)', result, "settings cmd does not work")

    def test_02_print_setting(self):
        result = cli_plug(None, 'set language')
        self.assertIn('language', result, 'print setting does not work')
        self.assertIn('Your system language', result, 'print setting does not work #2')

    def test_03_set_language(self):
        result = cli_plug(None, 'set language de')
        self.assertIn('setting for language changed', result, "Setting system language does not work #1")
        got = cli_gizmore().get_setting_val('language')
        self.assertEqual(got, 'de', 'Cannot set language to german.')
        cli_plug(None, 'set language en')

    def test_04_all_settings_web(self):
        out = web_plug('login.form.html').exec()
        out = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        out = web_plug('account.all_settings.html').exec()
        self.assertIn('Language', out, 'Language module not shown in all_settings().')

    def test_05_render_single_settings(self):
        out = web_plug('login.form.html').exec()
        out = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        out = web_plug('account.settings;module.language.html').exec()
        self.assertIn('Change Language settings', out, 'Module Language does not appear in account.settings(Language).')

    def test_06_change_single_setting(self):
        out = web_plug('login.form.html').exec()
        out = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        out = web_plug('account.settings;module.language.html').post({'language': 'de', 'submit_language': '1'}).exec()
        self.assertIn('de', out, 'Cannot change language settings #1.')
        out = web_plug('account.settings;module.language.html').post({'language': 'en', 'submit_language': '1'}).exec()
        self.assertIn('en', out, 'Cannot change language settings #2.')
        out = web_plug('account.settings;module.mail.html').post({'submit_mail': '1'}).exec()
        self.assertIn('submit_mail', out, 'Cannot save email settings.')


if __name__ == '__main__':
    unittest.main()
