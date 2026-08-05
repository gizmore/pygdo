import os
import unittest

from gdo.base.Application import Application
from gdo.base.Render import Mode, Render
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Connector import GDT_Connector
from gdo.core.connector.Web import Web
from gdo.core.connector.Bash import Bash
from gdo.core.method.servers import servers
from gdotest.TestUtil import cli_gizmore, cli_plug, GDOTestCase


class DogTestCase(GDOTestCase):
    """
    This are just some brief checks.
    The IRC Module has far better tests for a dog connector
    """

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_01_connector_gdt(self):
        gdt = GDT_Connector("conn").initial("web")
        conn = gdt.get_value()()
        self.assertIsInstance(conn, Web, "Cannot get initial Web connector")

    async def test_02_connector_add(self):
        num_servers = GDO_Server.table().count_where()
        out = cli_plug(None, f"$add_server web_{num_servers + 1} web http://" + Application.config('core.domain') + ":" + Application.config('core.port'))
        self.assertIn("web server has been added", out, "Cannot add second Web Connector Server")

    async def test_03_get_all_servers(self):
        servers = GDO_Server.table().all()
        self.assertGreater(len(servers), 1, "Cannot get servers.")

    async def test_04_server_status(self):
        web = Web.get_server()
        out = cli_plug(cli_gizmore(), f"$server {web.get_id()} status")
        self.assertIn(f"{web.get_name()}: up", out, "Cannot query a server's runtime status")

    async def test_05_servers_render_stable_ids(self):
        server = Bash.get_server()
        rendered = servers().render_gdo(server, Mode.render_irc)
        self.assertIn(Render.bold(server.get_id(), Mode.render_irc), rendered)
        self.assertIn(server.get_name(), rendered)


if __name__ == '__main__':
    unittest.main()
