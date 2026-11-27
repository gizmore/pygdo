import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.method.servers import servers


class ServersOptionsTest(unittest.TestCase):
    def test_search_disabled_pagination_retained(self):
        Application.mode(Mode.render_cli)
        method = servers()
        self.assertFalse(method.gdo_searched())
        self.assertTrue(method.gdo_paginated())

    def test_missing_connector_displays_unknown_without_instantiation(self):
        Application.mode(Mode.render_cli)
        server = MagicMock()
        server.get_id.return_value = '42'
        server.get_name.return_value = 'WhatsApp'
        server.get_connector_name.return_value = 'whatsapp'
        with patch('gdo.core.method.servers.Connector.get_by_name', return_value=None):
            result = servers().render_gdo(server, Mode.render_cli)
        self.assertIn('WhatsApp', result)
        self.assertIn('???', result)
        server.get_connector.assert_not_called()

    def test_registered_connector_still_uses_connection_state(self):
        Application.mode(Mode.render_cli)
        server = MagicMock()
        server.get_id.return_value = '1'
        server.get_name.return_value = 'IRC'
        server.get_connector_name.return_value = 'irc'
        server.get_connector.return_value.is_connected.return_value = True
        with patch('gdo.core.method.servers.Connector.get_by_name', return_value=object):
            result = servers().render_gdo(server, Mode.render_cli)
        self.assertIn('IRC', result)
        self.assertNotIn('???', result)
        server.get_connector.return_value.is_connected.assert_called_once()
