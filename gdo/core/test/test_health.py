import unittest
from gdotest.TestUtil import GDOTestCase

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.method.health import health


class HealthTest(GDOTestCase):

    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_health_is_owner_only(self):
        method = health()
        self.assertEqual('owner', method.gdo_user_permission())
