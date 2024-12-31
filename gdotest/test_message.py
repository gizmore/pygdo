import unittest
import os

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.message.GDT_Message import GDT_Message


class GDO_Foo(GDO):
    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_Message('foo_msg'),
        ]

class MessageTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    def test_01_composition(self):
        gdo = GDO_Foo.blank({
            'foo_msg_input': '<b>hello world!</b>',
        })
        gdt = gdo.column('foo_msg')
        self.assertIsInstance(gdt, GDT_Message, "Cannot get GDT_Message for GDO_Foo")


if __name__ == '__main__':
    unittest.main()
