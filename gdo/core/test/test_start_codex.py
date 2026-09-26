import subprocess
import unittest
from gdotest.TestUtil import GDOTestCase
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.method.start_codex import start_codex


class StartCodexTest(GDOTestCase):

    def setUp(self):
        Application.mode(Mode.render_cli)

    def test_is_owner_only(self):
        self.assertEqual('owner', start_codex().gdo_user_permission())

    @patch.object(start_codex, 'launcher_is_safe', return_value=True)
    @patch('gdo.core.method.start_codex.subprocess.Popen')
    def test_starts_only_the_fixed_non_root_launcher(self, popen, _):
        method = start_codex()
        method.reply = MagicMock(return_value='started')
        self.assertEqual('started', method.gdo_execute())
        popen.assert_called_once_with(
            ['/usr/local/bin/launch-mira-codex'],
            cwd='/home/gizmore',
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
