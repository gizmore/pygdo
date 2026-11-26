import unittest

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.method.servers import servers


class ServersOptionsTest(unittest.TestCase):
    def test_search_disabled_pagination_retained(self):
        Application.mode(Mode.render_cli)
        method = servers()
        self.assertFalse(method.gdo_searched())
        self.assertTrue(method.gdo_paginated())
