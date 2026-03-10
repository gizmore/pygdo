import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.net.GDT_IP import GDT_IP
from gdo.net.GDT_Url import GDT_Url
from gdotest.TestUtil import cli_plug, GDOTestCase


class NetTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_01_urls_basic(self):
        gdt = GDT_Url('url').initial('https://not_existing_domain_name_in_dns').reachable()
        url = gdt.get_value()
        self.assertEqual(url['port'], 443, "Cannot parse https port for quite invalid url.")
        self.assertEqual(url['host'], 'not_existing_domain_name_in_dns', "Cannot parse https host for quite invalid url.")
        gdt.validated()
        self.assertEqual(gdt._errkey, 'err_http_url_available', 'URL should be err_url_available.')

    async def test_02_working_website_url(self):
        gdt = GDT_Url('url').initial('https://www.wechall.net').reachable()
        self.assertIsNotNone(gdt.validated(), "Cannot validate existing IRC URL")

    async def test_03_ircs_urls(self):
        gdt = GDT_Url('url').initial('ircs://irc.wechall.net').all_schemes().reachable()
        self.assertIsNotNone(gdt.validated(), "Cannot validate existing IRC URL")
        url = gdt.get_value()
        self.assertEqual(url['port'], 6697, "Cannot parse ircs url for IRC url.")

    async def test_04_wget(self):
        out = cli_plug(None, "$wget https://www.wechall.net/")
        self.assertIn('Inferno', out, "WGET does not work")

    async def test_05_ip_binary(self):
        gdt = GDT_IP('bin').binary()
        ip4 = '192.168.0.1'
        gdt.value(ip4)
        bin = b'\xc0\xa8\x00\x01'
        self.assertEqual(bin, gdt.get_val(), 'IP4 binary no work.')
        ip6 = 'FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF'
        gdt.value(ip6)
        bin =  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        self.assertEqual(bin, gdt.get_val(), 'IP6 binary no work.')





if __name__ == '__main__':
    unittest.main()
