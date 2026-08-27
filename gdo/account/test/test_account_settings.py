import os
import unittest
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.date.GDO_Timezone import GDO_Timezone
from gdo.date.GDT_Timezone import GDT_Timezone
from gdo.language.GDT_Language import GDT_Language
from gdotest.TestUtil import cli_plug, reinstall_module, cli_gizmore, web_gizmore, web_plug, GDOTestCase, install_module


class AccountTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        ModuleLoader.instance().load_modules_db()
        install_module('account')
        Application.init_cli()
        ModuleLoader.instance().init_modules(True, True)
        ModuleLoader.instance().init_cli()

    def test_00_reinstall(self):
        reinstall_module('account')

    def test_01_settings(self):
        result = cli_plug(None, '$settings')
        self.assertIn('language(English)', result, "settings cmd does not work")

    def test_02_print_setting(self):
        result = cli_plug(None, '$set language')
        self.assertIn('language', result, 'print setting does not work')
        self.assertIn('Your setting for language', result, 'print setting does not work #2')

    def test_03_set_language(self):
        result = cli_plug(None, '$set language de')
        self.assertIn('setting for language changed', result, "Setting system language does not work #1")
        got = cli_gizmore().get_setting_val('language')
        self.assertEqual(got, 'de', 'Cannot set language to german.')
        cli_plug(None, '$set language en')

    def test_04_all_settings_web(self):
        out = web_plug('login.form.html').user('gizmore').exec()
        out = web_plug('login.form.html').user('gizmore').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        out = web_plug('account.all_settings.html').user('gizmore').exec()
        self.assertIn('Language', out, 'Language module not shown in all_settings().')
        self.assertIn('Connect another account', out, 'Account-connect link missing from user settings.')
        self.assertIn('user.connect', out, 'Account-connect URL missing from user settings.')

    def test_05_render_single_settings(self):
        out = web_plug('login.form.html').user('gizmore').exec()
        out = web_plug('login.form.html').user('gizmore').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        out = web_plug('account.settings.module.language.html').user('gizmore').exec()
        self.assertIn('Change Language settings', out, 'Module Language does not appear in account.settings(Language).')

    def test_06_change_single_setting(self):
        out = web_plug('login.form.html').exec()
        out = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        out = web_plug('account.settings.module.language.html').user('gizmore').post({'language': 'de', 'submit_language': '1'}).exec()
        self.assertIn('de', out, 'Cannot change language settings #1.')
        out = web_plug('account.settings.module.language.html').user('gizmore').post({'language': 'en', 'submit_language': '1'}).exec()
        self.assertIn('en', out, 'Cannot change language settings #2.')
        out = web_plug('account.settings.module.mail.html').user('gizmore').post({'submit_mail': '1'}).exec()
        self.assertIn('submit_mail', out, 'Cannot save email settings.')

    def test_07_save_user_setting_with_action_link(self):
        timezone = GDO_Timezone.get_by_name('Europe/Berlin')
        self.assertIn('Europe/Berlin', GDT_Timezone('timezone').display_var(timezone.get_id()))
        self.assertEqual('English', GDT_Language('language').display_var('en'))
        with patch('gdo.core.GDO_User.IPC.send'):
            out = web_plug('account.settings.module.user.html').user('gizmore').post({
                'about_me': 'Settings regression test',
                'submit_user': '1',
            }).exec()
            timezone_out = web_plug('account.settings.module.date.html').user('gizmore').post({
                'timezone': timezone.get_id(),
                'submit_date': '1',
            }).exec()
        self.assertIn('Settings regression test', out, 'User settings form did not retain its submitted value.')
        self.assertEqual('Settings regression test', web_gizmore().get_setting_val('about_me'))
        self.assertIn('Europe/Berlin', timezone_out, 'Timezone changes must display the timezone name.')


if __name__ == '__main__':
    unittest.main()
