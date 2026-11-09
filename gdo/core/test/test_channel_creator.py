import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Creator import GDT_Creator


class ChannelCreatorTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)
        self.server = GDO_Server()
        self.server.get_channel_by_name = MagicMock(return_value=None)

    def test_explicit_creator_is_not_overwritten(self):
        row = MagicMock()
        row._dirty = ['chan_creator']
        row._vals = {'chan_creator': '42'}
        creator = MagicMock()
        creator.get_name.return_value = 'chan_creator'
        GDT_Creator.gdo_before_create(creator, row)
        row.set_val.assert_not_called()

    def test_stale_creator_falls_back_to_system(self):
        self.check_creator([0, 1], '1')

    def test_existing_creator_is_preserved(self):
        self.check_creator([1], '42')

    def check_creator(self, counts, expected):
        user = MagicMock()
        user.is_persisted.return_value = True
        user.get_id.return_value = '42'
        users = MagicMock()
        users.quote.side_effect = lambda value: "'" + value + "'"
        users.count_where.side_effect = counts
        channel = MagicMock()
        with patch('gdo.core.GDO_Server.GDO_User.table', return_value=users), \
                patch('gdo.core.GDO_Channel.GDO_Channel.blank', return_value=channel) as blank, \
                patch.object(self.server, 'get_id', return_value='2'), \
                patch.object(self.server, 'get_trigger', return_value='$'), \
                patch.object(self.server, 'get_lang_iso', return_value='en'):
            self.server.get_or_create_channel('test', creator=user)
        self.assertEqual(expected, blank.call_args.args[0]['chan_creator'])

    def test_missing_system_user_is_reported(self):
        user = MagicMock()
        user.is_persisted.return_value = True
        user.get_id.return_value = '42'
        users = MagicMock()
        users.quote.side_effect = lambda value: "'" + value + "'"
        users.count_where.return_value = 0
        with patch('gdo.core.GDO_Server.GDO_User.table', return_value=users):
            with self.assertRaisesRegex(RuntimeError, 'system user 1 is missing'):
                self.server.get_or_create_channel('test', creator=user)
