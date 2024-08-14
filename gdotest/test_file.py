import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.file.GDT_FileUpload import GDT_FileUpload
from gdo.form.GDT_Form import GDT_Form, Encoding


class FileTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules()
        return self

    def test_01_multipart_enabled(self):
        form = GDT_Form()
        form.add_field(GDT_FileUpload('file'))
        self.assertEqual(form._encoding, Encoding.MULTIPART, 'form is not multipart.')
