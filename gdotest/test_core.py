import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_MD5 import GDT_MD5
from gdo.core.GDT_Path import GDT_Path


class CoreTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        loader.init_cli()

    def test_01_md5_string(self):
        hash = GDT_MD5.hash_for_str("abc")
        self.assertEqual(hash, '900150983cd24fb0d6963f7d28e17f72', "MD5 hashing of ABC failed horribly.")

    def test_02_md5_file(self):
        path = Application.file_path('DOCS/TESTAMENTUM.md')
        hash = GDT_MD5.hash_for_file(path)
        self.assertEqual(hash, '71c4ca68e7f80d367aa34723034e5d27', "MD5 hashing of testamentum file failed.")

    def test_03_path(self):
        gdt = GDT_Path('file').initial(Application.file_path('DOCS')).existing_dir()
        self.assertIsNotNone(gdt.validated(), "Checking GDT_File for an existing dir fails.")
        gdt = GDT_Path('file').initial(Application.file_path('DOCS/README.md')).existing_file()
        self.assertIsNotNone(gdt.validated(), "Checking GDT_File for an existing dir fails.")
        gdt = GDT_Path('file').initial(Application.file_path('DOCS/README_NOT.md')).existing_file()
        self.assertIsNone(gdt.validated(), "Checking GDT_File for an existing file should fail.")


if __name__ == '__main__':
    unittest.main()
