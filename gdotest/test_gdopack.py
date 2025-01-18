import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.WithSerialization import WithSerialization
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Dict import GDT_Dict
from gdo.install.Installer import Installer
from gdo.message.GDT_HTML import GDT_HTML
from gdotest.TestUtil import cli_gizmore, GDOTestCase, reinstall_module, install_module


class GDOPackTestCase(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        Cache.clear()
        install_module('core')
        loader = ModuleLoader.instance()
        Cache.clear()
        loader.reset()
        loader.load_modules_db(True)
        loader.init_modules()
        loader.init_cli()
        cli_gizmore()

    def test_01_pack_unpack(self):
        gdt = GDT_Dict(**{'foo': 'bar', 'eins': 1, 'zwo': GDT_Dict(**{'uff': 'hiya'})})
        packed = gdt.gdopack()
        self.assertIn(b'foo', packed, "Cannot pack GDT dict #1")
        self.assertIn(b'eins', packed, "Cannot pack GDT dict #2")
        self.assertIn(b'uff', packed, "Cannot pack GDT dict #3")
        gdt = WithSerialization.gdounpack(packed)
        self.assertIsInstance(gdt, GDT_Dict, 'Cannot unpack GDT dict #1')
        self.assertEqual('bar', gdt['foo'], 'Cannot unpack GDT dict #2')
        self.assertEqual('hiya', gdt['zwo']['uff'], 'Cannot unpack GDT dict #3')

    def test_02_pack_html(self):
        gdt = GDT_HTML().html('<h1>Test</h1>')
        packed = gdt.gdopack()
        gdt = WithSerialization.gdounpack(packed)
        self.assertEqual('<h1>Test</h1>', gdt.render(Mode.HTML), 'Cannot unpack GDT_HTML #1')

    def test_03_primitive_cache(self):
        Cache.set('a', 'b', 'c')
        d = Cache.get('a', 'b')
        self.assertEqual('c', d, 'cannot gdo pack str.')

    def test_04_system_user_cache(self):
        Cache.clear()
        gdo1 = GDO_User.system()
        gdo2 = GDO_User.table().get_by_id('1')
        self.assertEqual(gdo1, gdo2, 'GDO OCache not working #1')
        gdo3 = GDO_User.table().get_by_id('1')
        self.assertEqual(gdo3, gdo2, 'GDO OCache not working #2')

    def test_05_gdo_serial(self):
        Cache.clear()
        bash = GDO_Server.table().get_by_id('1')
        packed = bash.gdopack()
        unpack = WithSerialization.gdounpack(packed)
        self.assertEqual('1', unpack.get_id(), 'GDO does not serialize vals')


if __name__ == '__main__':
    unittest.main()
