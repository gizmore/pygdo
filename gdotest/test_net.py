import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.net.GDT_Url import GDT_Url


class NetTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        loader.init_cli()

    def test_01_urls_basic(self):
        gdt = GDT_Url('url').initial('https://not_existing_domain_name_in_dns').exists()
        url = gdt.get_value()
        self.assertEqual(url['port'], 443, "Cannot parse https port for quite invalid url.")
        self.assertEqual(url['host'], 'not_existing_domain_name_in_dns', "Cannot parse https host for quite invalid url.")
        gdt.validated()
        self.assertEqual(gdt._errkey, 'err_http_url_available', 'URL should be err_url_available.')

    def test_02_working_website_url(self):
        gdt = GDT_Url('url').initial('https://www.wechall.net').exists()
        self.assertIsNotNone(gdt.validated(), "Cannot validate existing IRC URL")

    def test_03_ircs_urls(self):
        gdt = GDT_Url('url').initial('ircs://irc.wechall.net').all_schemes().exists()
        self.assertIsNotNone(gdt.validated(), "Cannot validate existing IRC URL")
        url = gdt.get_value()
        self.assertEqual(url['port'], 6697, "Cannot parse ircs url for IRC url.")


if __name__ == '__main__':
    unittest.main()
