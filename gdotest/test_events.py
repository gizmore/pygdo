import asyncio
import os
import time
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdotest.TestUtil import GDOTestCase


class EventsTestCase(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        Application.init_cli()
        ModuleLoader.instance().load_modules_db()
        ModuleLoader.instance().init_modules()
        ModuleLoader.instance().init_cli()

    def test_01_events(self):
        y = 0

        def foo(x):
            nonlocal y
            y += x

        Application.EVENTS.subscribe('test_event', foo)
        Application.EVENTS.publish('test_event', 1)
        Application.EVENTS.publish('test_event', 1)
        self.assertEqual(y, 2, 'basic event publishing does not work')

        Application.EVENTS.reset_all()

        Application.EVENTS.subscribe_once('test_event', foo)
        Application.EVENTS.publish('test_event', 1)
        Application.EVENTS.publish('test_event', 1)
        self.assertEqual(y, 3, 'basic event once publishing does not work')

        Application.EVENTS.reset_all()

    def test_02_timers(self):
        y = 0
        def tck():
            Application.tick()
            asyncio.run(Application.EVENTS.update_timers(Application.TIME))
        async def foo():
            nonlocal y
            y += 1
        Application.EVENTS.add_timer(0.25, foo, 2)
        tck()
        time.sleep(0.25)
        tck()
        time.sleep(0.25)
        tck()
        time.sleep(0.25)
        tck()
        time.sleep(0.25)
        tck()
        self.assertEqual(y, 2, 'Timers do not fire correctly')

if __name__ == '__main__':
    unittest.main()
