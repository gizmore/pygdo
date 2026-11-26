import unittest
from unittest.mock import MagicMock, call, patch

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.install.Installer import Installer


class WipeNoRedisTest(unittest.TestCase):
    def test_redis_lookup_returns_miss_without_redis(self):
        obj = MagicMock()
        obj.gdo_cached.return_value = True
        with patch.object(Cache, 'RCACHE', None):
            self.assertIsNone(Cache.obj_search_redis(obj, {'key': 'value'}))

    def test_wipe_propagates_error_and_restores_foreign_keys(self):
        db, module = MagicMock(), MagicMock()
        with patch.object(Application, 'db', return_value=db), \
             patch.object(Installer, 'wipe_configuration', side_effect=RuntimeError('failure')), \
             patch('gdo.install.Installer.Logger.exception'):
            with self.assertRaisesRegex(RuntimeError, 'failure'):
                Installer.wipe(module)
        self.assertEqual([call(False), call(True)], db.foreign_keys.call_args_list)
        module.delete.assert_not_called()
