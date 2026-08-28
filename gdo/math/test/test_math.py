import os

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.math.GDT_MathExpression import GDT_MathExpression
from gdo.math.method.calc import calc
from gdotest.TestUtil import GDOTestCase, install_module


class MathTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()
        loader = ModuleLoader.instance()
        install_module('math')
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_01_calculator_complexity_limits(self):
        field = GDT_MathExpression('expression')
        self.assertTrue(field.validate('sin(pi / 2)'))
        self.assertTrue(field.validate('3**2'))
        self.assertFalse(field.validate('10**10**10'))
        self.assertFalse(field.validate('2**129'))

    async def test_02_calculator_requires_voice(self):
        self.assertEqual('voice', calc().gdo_permission())
