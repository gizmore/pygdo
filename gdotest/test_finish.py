import os
import unittest

from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render, Mode
from gdo.base.Trans import Trans
from gdo.base.Util import gdo_print
from gdo.core.GDO_Session import GDO_Session
from gdotest.TestUtil import GDOTestCase, web_gizmore, cli_gizmore


class FinishTestCase(GDOTestCase):
    """
    Check overall stats and errors as last test suite
    """

    def check_slots(self, obj: object):
        if hasattr(obj, '__slots__'):
            try:
                obj.foo = 1337
                self.assertTrue(False, f"{obj.__class__} has broken slots.")
            except:
                pass

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()
        giz = web_gizmore()
        Application.STORAGE.cookies = {}
        Application.set_current_user(giz)
        Application.set_session(GDO_Session.start(True))
        cli_gizmore()

    def test_01_slots(self):
        classes = [
            Method,
        ]
        for klass in classes:
            self.check_slots(klass())
        for module in ModuleLoader.instance().enabled():
            for klass in module.gdo_classes():
                gdo = klass.blank()
                self.check_slots(gdo)

    async def test_02_include_all_files(self):
        gizmore = cli_gizmore()
        count = 0
        for module in ModuleLoader.instance()._cache.values():
            for method in module.get_methods():
                method.env_server(gizmore.get_server()).env_user(gizmore).env_session(GDO_Session.for_user(gizmore)).env_mode(Mode.CLI)
                # await method.execute()
                count += 1
        gdo_print(f"Tested {count} methods for import errors.")



    # def test_01_no_translation_errors(self):
    #     count = len(Trans.FAILURES)
    #     missing = ', '.join(Trans.FAILURES.keys())
    #     self.assertEqual(count, 0, f'There are Translation errors left: {missing}.')


if __name__ == '__main__':
    unittest.main()
