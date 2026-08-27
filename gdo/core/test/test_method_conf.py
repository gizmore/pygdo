import unittest
from unittest.mock import MagicMock

from gdo.base.Application import Application
from gdo.core.MethodConf import MethodConf


class DummyConf(MethodConf):

    def get_configs(self, method):
        return []

    def get_config(self, method, key):
        return self.conf

    def get_config_val(self, method, key):
        return 'override'

    def set_config_val(self, method, key, val):
        self.set_value(key, val)

    def delete_config_val(self, method, key):
        self.delete_value(key)


class MethodConfTest(unittest.TestCase):

    def setUp(self):
        Application.init_common()

    def test_null_deletes_the_override_and_uses_initial_value(self):
        command = DummyConf()
        command.conf = MagicMock()
        command.conf.get_name.return_value = 'enabled'
        command.conf.get_initial.return_value = '0'
        command.conf.display_var.side_effect = lambda value: value
        command.delete_value = MagicMock()
        command.set_value = MagicMock()
        command.reply = MagicMock()
        method = MagicMock()
        method.gdo_trigger.return_value = 'confs'

        command.set_config(method, 'enabled', 'NULL')

        command.delete_value.assert_called_once_with('enabled')
        command.set_value.assert_not_called()
