import os
import unittest
from unittest.mock import patch

from gdo.base.Application import Application


class LogConfigTest(unittest.TestCase):
    def test_relative_log_directory(self):
        with patch.object(Application, 'PATH', '/srv/pygdo/'), \
             patch.object(Application, 'config', return_value='protected/logs_tes'), \
             patch('gdo.base.Application.Logger.init') as init:
            Application.init_log_directory()
        init.assert_called_once_with('/srv/pygdo/protected/logs_tes/')

    def test_absolute_log_directory(self):
        with patch.object(Application, 'PATH', '/srv/pygdo/'), \
             patch.object(Application, 'config', return_value='/var/log/pygdo'), \
             patch('gdo.base.Application.Logger.init') as init:
            Application.init_log_directory()
        init.assert_called_once_with('/var/log/pygdo/')

    def test_default_log_directory(self):
        with patch.object(Application, 'PATH', '/srv/pygdo/'), \
             patch.object(Application, 'CONFIG', {}), \
             patch('gdo.base.Application.Logger.init') as init:
            Application.config.cache_clear()
            try:
                Application.init_log_directory()
            finally:
                Application.config.cache_clear()
        init.assert_called_once_with(os.path.join('/srv/pygdo/', 'protected/logs/', ''))
