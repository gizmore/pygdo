import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import bytelen
from gdo.core import module_core
from gdo.core.method.echo import echo
from gdotest.TestUtil import WebPlug


class WebTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules()
        return self

    def test_01_web_method_loader(self):
        loader = ModuleLoader.instance()
        method = loader.get_module('core').get_method('echo')
        self.assertIsInstance(method, echo, "Cannot load method echo via web means")

    def test_02_web_plug_echo(self):
        req = WebPlug("core.echo;text.This%20Test.html?_lang=de")
        req.exec()
        self.assertIn('This Test', req._out, "Plugged web test failed")

    def test_03_json_via_web(self):
        req = WebPlug("core.echo;text.This%20Test.json?_lang=de")
        req.exec()
        self.assertIn('{', req._out, "web json test failed")
        self.assertIn('"text":', req._out, "web json test failed")
        self.assertIn('"This Test"', req._out, "web json test failed")
        self.assertIn('}', req._out, "web json test failed")

    def test_04_welcome_page(self):
        req = WebPlug("core.welcome.html")
        req.exec()
        self.assertIn('PyGDO', req._out, "Welcome method does not work")

    def test_05_file_not_found(self):
        req = WebPlug("core.echoNONO;This%20Test.html?_lang=de")
        req.exec()
        self.assertIn('not found', req._out, "Plugged web test 404 failed")

    def test_06_asset_download(self):
        req = WebPlug("gdo/core/css/pygdo.css?v=2")
        out = req.exec()
        self.assertIn('margin:', out, "CSS asset pygdo.css cannot be served by web handler.")

    def test_07_web_path_echo_cli(self):
        req = WebPlug("core.echo;text.This.is.a.test.cli")
        out = req.exec()
        self.assertEqual('This.is.a.test', out, "CLI echo does not work properly")

    def test_08_web_path_echo_txt(self):
        req = WebPlug("core.echo;text.This.is.a.test.txt")
        out = req.exec()
        self.assertEqual('This.is.a.test', out, "TXT echo does not work properly")

    def test_09_benchmark_bytelen(self):
        test_string = "Totally Ö and Ü" * 1000
        self.assertEqual(bytelen(test_string), len(test_string.encode('UTF-8')), 'bytelen function does not give correct result')

    def test_10_perf(self):
        core = module_core.instance()
        self.assertTrue(core.should_show_perf(), "Perf is not wanted but it should be")


if __name__ == '__main__':
    unittest.main()
