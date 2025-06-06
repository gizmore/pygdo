import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.connector.Web import Web
from gdotest.TestUtil import cli_plug, GDOTestCase


class DogTestCase(GDOTestCase):
    """
    This are just some brief checks.
    The IRC Module has far better tests for a dog connector
    """

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)
        loader.init_cli()

    def test_01_connector_gdt(self):
        gdt = GDT_Connector("conn").initial("web")
        conn = gdt.get_value()
        self.assertIsInstance(conn, Web, "Cannot get initial Web connector")

    def test_02_connector_add(self):
        num_servers = GDO_Server.table().count_where()
        out = cli_plug(None, f"$add_server web_{num_servers + 1} web http://" + Application.config('core.domain') + ":" + Application.config('core.port'))
        self.assertIn("web server has been added", out, "Cannot add second Web Connector Server")

    def test_03_get_all_servers(self):
        servers = GDO_Server.table().all()
        self.assertGreater(len(servers), 1, "Cannot get servers.")


if __name__ == '__main__':
    unittest.main()
