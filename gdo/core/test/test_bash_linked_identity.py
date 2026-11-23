import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


spec = importlib.util.spec_from_file_location(
    'pygdo_cli_under_test', Path(__file__).resolve().parents[3] / 'bin' / 'pygdo.py')
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class BashLinkedIdentityTest(unittest.TestCase):
    def test_real_local_user_uses_linked_identity_without_inheriting_authentication(self):
        origin = MagicMock()
        origin.get_name.return_value = 'gizmore'
        origin.is_authenticated.return_value = False
        master = SimpleNamespace(_authenticated=True, name='web')
        origin.get_effective_user.return_value = master
        with patch.object(cli.os, 'geteuid', return_value=1000), \
                patch.object(cli.pwd, 'getpwuid', return_value=SimpleNamespace(pw_name='gizmore')):
            resolved = cli.cli_effective_user(origin)
        self.assertEqual('web', resolved.name)
        self.assertFalse(resolved._authenticated)
        self.assertTrue(master._authenticated)

    def test_other_local_user_cannot_inherit_linked_identity(self):
        origin = MagicMock()
        origin.get_name.return_value = 'gizmore'
        with patch.object(cli.os, 'geteuid', return_value=1001), \
                patch.object(cli.pwd, 'getpwuid', return_value=SimpleNamespace(pw_name='other')):
            self.assertIs(origin, cli.cli_effective_user(origin))
        origin.get_effective_user.assert_not_called()
