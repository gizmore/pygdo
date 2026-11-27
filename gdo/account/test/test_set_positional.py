from unittest.mock import patch

from gdo.account.method.set_cli import set_cli
from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Render import Mode
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdotest.TestUtil import GDOTestCase


class SetPositionalTest(GDOTestCase):
    def setUp(self):
        Cache.init()
        Application.mode(Mode.render_cli)

    def test_name_and_value_are_optional_positionals(self):
        with patch.object(GDT_UserSetting, 'KNOWN', {'language': GDT_String('language')}):
            for args, expected_name, expected_value in [([], None, None),
                    (['language'], 'language', None), (['language', 'ar'], 'language', 'ar')]:
                with self.subTest(args=args):
                    method = set_cli()
                    method._raw_args.pargs = args
                    params = method.parameters()
                    self.assertFalse(params['name'].is_not_null())
                    self.assertTrue(params['name'].is_positional())
                    self.assertEqual(expected_name, params['name'].get_val())
                    self.assertEqual(expected_value, params['value'].get_val())
