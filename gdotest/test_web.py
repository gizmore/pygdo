import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.method.echo import echo
from gdotest.TestUtil import WebPlug
from index import handler


class WebTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules()
        return self

    def test_web(self):
        loader = ModuleLoader.instance()
        method = loader.get_module('core').get_method('echo')
        self.assertIsInstance(method, echo, "Cannot load method echo via web means")

    def test_plug(self):
        req = WebPlug("core.echo;text.This%20Test.html?_lang=de")
        handler(req)
        self.assertIn('This Test', req._out, "Plugged web test failed")

    def test_welcome(self):
        req = WebPlug("core.welcome.html")
        handler(req)
        self.assertIn('GDO', req._out, "Plugged web test failed")

    def test_file_not_found(self):
        req = WebPlug("core.echoNONO;This%20Test.html?_lang=de")
        handler(req)
        self.assertIn('not found', req._out, "Plugged web test 404 failed")

    def test_asset_download(self):
        req = WebPlug("gdo/core/css/pygdo.css?v=2")
        handler(req)
        self.assertIn('margin:', req._out, "CSS asset pygdo.css cannot be served by web handler.")


if __name__ == '__main__':
    unittest.main()
