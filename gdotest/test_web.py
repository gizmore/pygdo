import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import bytelen
from gdo.core.method.echo import (echo)
from gdotest.TestUtil import WebPlug, GDOTestCase, web_gizmore


class WebTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)
        Application.init_cli()

    async def test_01_web_method_loader(self):
        loader = ModuleLoader.instance()
        method = loader.get_module('core').get_method('echo')
        self.assertIsInstance(method, echo, "Cannot load method echo via web means")

    def test_02_web_plug_echo(self):
        req = WebPlug("core.echo;text~This%20Test.html?_lang=de")
        out = req.exec()
        self.assertIn('This Test', out, "Plugged web test failed")

    def test_03_json_via_web(self):
        req = WebPlug("core.echo;text~This%20Test.json?_lang=de")
        out = req.exec()
        self.assertIn('{', out, "web json test failed")
        self.assertIn('"text":', out, "web json test failed")
        self.assertIn('"This Test"', out, "web json test failed")
        self.assertIn('}', out, "web json test failed")

    async def test_04_welcome_page(self):
        req = WebPlug("core.welcome.html")
        out = req.exec()
        self.assertIn('PyGDO', out, "Welcome method does not work")

    async def test_05_file_not_found(self):
        req = WebPlug("core.echoNONO;This%20Test.html?_lang=de")
        out = req.exec()
        self.assertIn('not found', out, "Plugged web test 404 failed")

    async def test_06_asset_download(self):
        req = WebPlug("gdo/core/css/pygdo.css?v=2")
        out = req.exec()
        self.assertIn('margin:', out, "CSS asset pygdo.css cannot be served by web handler.")

    def test_07_web_path_echo_cli(self):
        req = WebPlug("core.echo;text~This.is.a.test.cli")
        out = req.exec()
        self.assertEqual('This.is.a.test', out, "CLI echo does not work properly")

    def test_08_web_path_echo_txt(self):
        req = WebPlug("core.echo;text~This.is.a.test.txt")
        out = req.exec()
        self.assertEqual('This.is.a.test', out, "TXT echo does not work properly")

    async def test_09_benchmark_bytelen(self):
        test_string = "Totally Ö and Ü" * 1000
        self.assertEqual(bytelen(test_string), len(test_string.encode('UTF-8')), 'bytelen function does not give correct result')

    async def test_11_connector_not_allowed(self):
        result = WebPlug("core.help.html").user('gizmore').exec()
        self.assertIn("does not work inside this connector", result, "A non Web Method is executing in HTTP.")


if __name__ == '__main__':
    unittest.main()
