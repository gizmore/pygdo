import unittest
import os

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.install.Installer import Installer
from gdo.message.GDT_Message import GDT_Message
from gdotest.TestUtil import GDOTestCase


class GDO_Foo(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('foo_id'),
            GDT_Message('foo_msg').label_raw('MSG'),
        ]

class MessageTestCase(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()
        Application.db().drop_table(GDO_Foo.table().gdo_table_name())
        Installer.install_gdo(GDO_Foo)

    def test_01_composition(self):
        gdo = GDO_Foo.blank({
            'foo_msg': '<b><i>hello world!</i></b>',
        })
        gdt = gdo.column('foo_msg')
        self.assertIsInstance(gdt, GDT_Message, "Cannot get GDT_Message for GDO_Foo")
        out = gdt.render(Mode.MARKDOWN)
        self.assertIn('***hello world!***', out, "Message markdown is broken")
        out = gdt.render(Mode.CLI)
        self.assertIn('\x1b[1m\x1b[3mhello world!\x1b[0m\x1b[0m', out, "Message cli is broken")
        out = gdt.render(Mode.FORM)
        self.assertIn('<textarea', out, "Message form is broken")

if __name__ == '__main__':
    unittest.main()
