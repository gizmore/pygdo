import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.WithSerialization import WithSerialization
from gdo.core.GDT_Dict import GDT_Dict
from gdotest.TestUtil import cli_gizmore, GDOTestCase


class GDOPackTestCase(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
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


if __name__ == '__main__':
    unittest.main()
