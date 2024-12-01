import json
import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Permutations
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Path import GDT_Path
from gdo.core.GDT_User import GDT_User
from gdo.core.connector.Bash import Bash
from gdo.core.method.reload import reload
from gdo.ui.GDT_Page import GDT_Page
from gdotest.TestUtil import cli_plug, web_gizmore, cli_gizmore, GDOTestCase


class CoreTestCase(GDOTestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        loader.init_cli()
        web_gizmore()
        cli_gizmore()
        super().setUp()

    def test_01_md5_string(self):
        hash = GDT_MD5.hash_for_str("abc")
        self.assertEqual(hash, '900150983cd24fb0d6963f7d28e17f72', "MD5 hashing of ABC failed horribly.")

    def test_02_md5_file(self):
        path = Application.file_path('DOCS/TESTAMENTUM.md')
        hash = GDT_MD5.hash_for_file(path)
        self.assertEqual(hash, 'fdd53b0e66e073d3b100c098010e3f09', "MD5 hashing of testamentum file failed.")

    def test_03_path(self):
        gdt = GDT_Path('file').initial(Application.file_path('DOCS')).existing_dir()
        self.assertIsNotNone(gdt.validated(), "Checking GDT_File for an existing dir fails.")
        gdt = GDT_Path('file').initial(Application.file_path('DOCS/README.md')).existing_file()
        self.assertIsNotNone(gdt.validated(), "Checking GDT_File for an existing dir fails.")
        gdt = GDT_Path('file').initial(Application.file_path('DOCS/README_NOT.md')).existing_file()
        self.assertIsNone(gdt.validated(), "Checking GDT_File for an existing file should fail.")

    def test_04_float_rendering(self):
        gdt = GDT_Float('number').initial_value(31337.141569)
        self.assertEqual(gdt.render_txt(), "31,337.142", "Float renders not nice Tryout #1")
        self.assertEqual(gdt.precision(6).render_txt(), "31,337.141569", "Float renders not nice Tryout #1")
        self.assertEqual(gdt.no_thousands().render_txt(), "31337.141569", "Float renders not nice Tryout #1")

    def test_05_clear_cache(self):
        cli_plug(None, "$cc")

    def test_06_permutations(self):
        values = [[1, 2], [3], [4, 5, 6]]
        correct = [
            [1, 3, 4],
            [2, 3, 4],
            [1, 3, 5],
            [2, 3, 5],
            [1, 3, 6],
            [2, 3, 6],
        ]
        perms = Permutations(values)
        i = 0
        for gen in perms.generate():
            self.assertEqual(gen, correct[i], f"Permutation generator failed.")
            i += 1

    def test_08_gdt_user(self):
        gdt = GDT_User('test')
        user = gdt.to_value('1')
        self.assertEqual(user.get_id(), '1', 'get_system_user via GDT_User failed.')

        giz = gdt.to_value('giz')
        self.assertEqual('err_select_candidates', gdt._errkey, 'get gizmore user via GDT_User should be ambiguous.')

        gdt.same_server()
        giz = gdt.to_value('giz')
        self.assertIsNotNone(giz, 'Cannot get giz on same server.')

    def test_09_db_debug(self):
        GDO_User.table().select().first().debug().exec()
        result = GDT_Page.instance()._top_bar.render()
        self.assertIn('SELECT * FROM gdo_user', result, 'Database Debug output does not render.')

    def test_10_reload_restricted(self):
        petra = Bash.get_server().get_or_create_user('Petra')
        method = reload().env_user(petra)
        has = method.has_permission(petra)
        self.assertEqual(has, False, "Permission check is not working")
        out = cli_plug(petra, "$reload")
        self.assertIn('ermission', out, "CLI Permission not working")

    def test_11_help(self):
        petra = Bash.get_server().get_or_create_user('Petra')
        out = cli_plug(petra, "$help")
        self.assertIn("31mreload", out, "Reload should be red")

    def test_12_whoami(self):
        out = cli_plug(cli_gizmore(), "$WHOAMI")
        self.assertIn('gizmore{1}', out, '$WHOAMI does not work')



if __name__ == '__main__':
    unittest.main()
