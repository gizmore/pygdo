import unittest
from unittest.mock import MagicMock, patch

from gdo.core.GDO_Server import GDO_Server


class ServerConnectorLookupTest(unittest.TestCase):
    def test_missing_then_late_registered_connector(self):
        server = GDO_Server()
        server._vals = {'serv_name': 'WhatsApp', 'serv_connector': 'whatsapp'}
        connector = MagicMock()
        factory = MagicMock(return_value=connector)
        with patch('gdo.core.GDO_Server.Connector.get_by_name', side_effect=[None, factory]) as lookup:
            with self.assertRaisesRegex(LookupError, 'whatsapp.*WhatsApp'):
                server.get_connector()
            self.assertIs(connector, server.get_connector())
            self.assertIs(connector, server.get_connector())
        self.assertEqual(2, lookup.call_count)
        factory.assert_called_once_with()
        connector.server.assert_called_once_with(server)

    def test_empty_connector_name_has_helpful_error(self):
        server = GDO_Server()
        server._vals = {'serv_name': 'empty', 'serv_connector': None}
        with self.assertRaisesRegex(LookupError, 'empty'):
            server.get_connector()
