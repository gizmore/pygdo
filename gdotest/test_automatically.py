import asyncio
import os
import unittest
from asyncio import iscoroutine

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOParamError
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Util import Permutations
from gdo.core.GDO_Server import GDO_Server
from gdotest.TestUtil import GDOTestCase, web_gizmore


class test_automatically(GDOTestCase):

    FAILED: int = 0

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules(True, True)
        Application.init_cli()

    async def test_01_test_defaults(self):
        for module in ModuleLoader.instance()._cache.values():
            for method in module.get_methods():
                self.method_test(method)
        self.assertEqual(0, self.FAILED, "Some automatic tests failed.")

    def method_test(self, method: Method):
        failed = False
        try:
            method.env_user(web_gizmore(), True)
            method.env_server(GDO_Server.get_by_connector('web'))
            test_vals = []
            for gdt in method.parameters():
                test_vals.append(gdt.get_test_vals())
            p = Permutations(test_vals)
            for val in p.generate():
                for gdt in method.parameters():
                    gdt.val(val)
                result = method.gdo_execute()
                while iscoroutine(result):
                    result = asyncio.run(result)
                result.render(Mode.render_html)
                result.render(Mode.render_form)
                result.render(Mode.render_txt)
                result.render(Mode.render_json)
        except GDOParamError:
            pass
        except Exception as ex:
            Logger.exception(ex)
            self.FAILED += 1


if __name__ == '__main__':
    unittest.main()
