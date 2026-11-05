import re
import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.core.GDT_User import GDT_User


class FakeQuery:
    def __init__(self, users):
        self.users, self.conditions, self.maximum = users, [], None

    def where(self, condition):
        self.conditions.append(condition)
        return self

    def limit(self, count):
        self.maximum = count
        return self

    def exec(self):
        return self

    def fetch_all(self):
        users = self.users
        for condition in self.conditions:
            if condition == '1=0':
                return []
            server = re.fullmatch(r'user_server=(\d+)', condition)
            uid = re.fullmatch(r'user_id=(\d+)', condition)
            if server:
                users = [u for u in users if u.get_server_id() == server.group(1)]
            elif uid:
                users = [u for u in users if u.get_id() == uid.group(1)]
            elif 'user_displayname' in condition:
                value = re.search(r"user_displayname(?:=| LIKE )'([^']*)'", condition).group(1)
                if value.startswith('%'):
                    users = [u for u in users if value.strip('%') in u.get_name().lower()]
                elif value.endswith('%'):
                    users = [u for u in users if u.get_name().lower().startswith(value[:-1])]
                else:
                    users = [u for u in users if u.get_name().lower() == value]
        return users[:self.maximum] if self.maximum is not None else users


class ScopedUserTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)
        self.server = MagicMock()
        self.server.get_id.return_value = '10'
        self.local = self.user('1', '10', 'tina-chan')
        self.remote = self.user('2', '20', 'tina-chan')
        self.local_other = self.user('3', '10', 'tina-chan-onair')
        self.remote_only = self.user('4', '20', 'paul')
        self.table = MagicMock()
        self.table.select.side_effect = lambda: FakeQuery([self.local, self.remote, self.local_other, self.remote_only])
        self.patches = [patch('gdo.core.GDO_User.GDO_User.table', return_value=self.table),
                        patch.object(GDT_User, 'with_completion', return_value=None)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    @staticmethod
    def user(uid, server, name):
        result = MagicMock()
        result.get_id.return_value = uid
        result.get_server_id.return_value = server
        result.get_name.return_value = name
        result.get_name_sid.return_value = f'{name}{{{server}}}'
        result.render_name.return_value = name
        return result

    def test_method_passes_request_server_and_exact_name_wins(self):
        class Send(Method):
            def gdo_parameters(self):
                return [GDT_User('to').not_null().positional()]

        method = Send()
        method._env_server = self.server
        method._raw_args.add_cli_line(['tina-chan'])
        self.assertIs(method.param_value('to'), self.local)

    def test_lax_server_explicitly_allows_cross_server_matches(self):
        field = GDT_User('to').server_context(self.server).lax_server()
        self.assertEqual(field.query_gdos('tina-chan'), [self.local, self.remote])
        field.error = MagicMock()
        self.assertIsNone(field.get_by_name('tina-chan'))
        field.error.assert_called_once()

    def test_remote_only_exact_and_prefix_still_work_by_default(self):
        field = GDT_User('to').server_context(self.server)
        self.assertIs(field.get_by_name('paul'), self.remote_only)
        self.assertIs(field.get_by_name('pau'), self.remote_only)

    def test_explicit_server_qualifier_and_numeric_ids(self):
        field = GDT_User('to').server_context(self.server)
        with patch('gdo.core.GDO_Server.GDO_Server.table') as servers:
            remote_server = MagicMock()
            remote_server.get_id.return_value = '20'
            servers.return_value.get_by_vals.return_value = remote_server
            self.assertEqual(field.query_gdos('tina-chan{rizon}'), [self.remote])
        self.assertEqual(field.query_gdos('2'), [self.remote])
        self.assertEqual(field.same_server().query_gdos('2'), [])
