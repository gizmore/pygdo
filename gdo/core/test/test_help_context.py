import unittest
from unittest.mock import Mock

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.base.Exceptions import GDODBException
from gdo.core.method.help import help


class HelpContextTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_repl_help_without_message(self):
        method = help()
        method.get_trigger = Mock(return_value='snapvid')
        method.show_help_for = Mock(return_value='help output')
        self.assertEqual('help output', method.gdo_execute())
        method.show_help_for.assert_called_once_with('snapvid')

    def test_channel_help_replies_privately(self):
        method = help()
        method._message = Mock()
        method._message._env_channel = object()
        method.get_trigger = Mock(return_value='snapvid')
        method.show_help_for = Mock(return_value='help output')
        self.assertEqual('help output', method.gdo_execute())
        method._message.reply_privately.assert_called_once_with(notice=True)

    def test_listing_survives_unavailable_method_table(self):
        from unittest.mock import patch

        command = Mock()
        command.gdo_module.return_value.render_name.return_value = 'forum'
        command.allows_connector.return_value = True
        command.gdo_method_hidden.return_value = False
        command.gdo_trigger.return_value = 'forum.reply'
        command.has_permission.side_effect = GDODBException('missing table', 'SELECT')
        loader = Mock()
        loader._methods = {'forum.reply': lambda: command}
        method = help()
        method._env_user = Mock()
        method.param_value = Mock(return_value=False)
        with patch('gdo.core.method.help.ModuleLoader.instance', return_value=loader):
            result = method.show_all_commands()
        self.assertIsNotNone(result)
        command.has_permission.assert_called_once()

    def test_general_help_hides_individual_video_commands(self):
        from unittest.mock import patch
        commands = []
        for module_name, trigger in (('video', 'video'), ('video', 'video.zap'), ('audio', 'audio'), ('audio', 'audio.say')):
            command = Mock()
            command.gdo_module.return_value.get_name = module_name
            command.gdo_module.return_value.render_name.return_value = module_name.title()
            command.gdo_trigger.return_value = trigger
            command.allows_connector.return_value = True
            command.gdo_method_hidden.return_value = trigger != module_name
            command.has_permission.return_value = True
            commands.append(command)
        loader = Mock()
        loader._methods = {str(i): (lambda command=command: command) for i, command in enumerate(commands)}
        method = help()
        method._env_user = Mock()
        method.param_value = Mock(return_value=False)
        with patch('gdo.core.method.help.ModuleLoader.instance', return_value=loader):
            method.show_all_commands()
        commands[0].has_permission.assert_called_once()
        commands[1].has_permission.assert_not_called()
        commands[2].has_permission.assert_called_once()
        commands[3].has_permission.assert_not_called()

    def test_default_hidden_hook_uses_module_policy(self):
        from gdo.base.Method import Method
        method = Method()
        module = Mock()
        module.get_name = 'audio'
        module.gdo_compact_text_help = True
        method.gdo_module = Mock(return_value=module)
        method.gdo_trigger = Mock(return_value='audio.say')
        self.assertTrue(method.gdo_method_hidden())
        method.gdo_trigger.return_value = 'audio'
        self.assertFalse(method.gdo_method_hidden())
