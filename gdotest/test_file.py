import os

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.form.GDT_Form import GDT_Form, Encoding
from gdotest.TestUtil import GDOTestCase


class FileTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_01_multipart_enabled(self):
        form = GDT_Form()
        form.add_field(GDT_FileUpload('file'))
        self.assertEqual(form._encoding, Encoding.MULTIPART, 'form is not multipart.')
