import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader


class EventsTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()
        ModuleLoader.instance().init_cli()
        return self

    def test_01_events(self):
        y = 0

        def foo(x):
            nonlocal y
            y = x

        Application.EVENTS.subscribe('test_event', foo)
        Application.EVENTS.publish('test_event', 1)
        self.assertEqual(y, 1, 'basic event publishing does not work')


if __name__ == '__main__':
    unittest.main()
