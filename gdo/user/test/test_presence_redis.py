from unittest.mock import Mock, patch

from redis.exceptions import RedisError

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.core.GDO_User import GDO_User
from gdo.user.module_user import module_user
from gdotest.TestUtil import GDOTestCase


class RedisPresenceTest(GDOTestCase):
    def setUp(self):
        self.redis = Mock()
        self.data = {}
        self.redis.get.side_effect = lambda key: self.data.get(key)
        self.redis.exists.side_effect = lambda key: key in self.data

        def set_key(key, value, **options):
            if options.get('nx') and key in self.data:
                return False
            self.data[key] = value
            return True

        def release(script, count, key, token):
            if self.data.get(key) == token:
                del self.data[key]
                return 1
            return 0

        self.redis.set.side_effect = set_key
        self.redis.eval.side_effect = release
        self.user = Mock()
        self.user.is_ghost.return_value = False
        self.user.is_persisted.return_value = True
        self.user.get_id.return_value = '42'
        self.module = module_user()

    def test_writes_are_per_user_and_not_rounded(self):
        with patch.object(Cache, 'RCACHE', self.redis), \
             patch.object(Application, 'config', return_value='test'), \
             patch.object(self.module, 'cfg_activity_accuracy', return_value=300), \
             patch('gdo.user.module_user.Time.get_date', side_effect=lambda t: str(t)), \
             patch.object(Application, 'TIME', 1001):
            self.module.set_last_activity(self.user)
            Application.TIME = 1200
            self.module.set_last_activity(self.user)
            self.assertEqual(1, self.user.save_setting.call_count)
            Application.TIME = 1301
            self.module.set_last_activity(self.user)
            self.assertEqual([('last_activity', '1001'), ('last_activity', '1301')],
                             [call.args for call in self.user.save_setting.call_args_list])
            self.assertEqual('1301', self.data['gdo:test:user:presence:42:seen'])
            self.assertEqual('1301', self.data['gdo:test:user:presence:42:written'])
            self.redis.set.assert_any_call('gdo:test:user:presence:42:seen', '1301', ex=360)

    def test_failed_save_does_not_mark_written(self):
        self.user.save_setting.side_effect = RuntimeError('database failed')
        with patch.object(Cache, 'RCACHE', self.redis), \
             patch.object(Application, 'config', return_value='test'), \
             patch.object(self.module, 'cfg_activity_accuracy', return_value=300), \
             patch.object(Application, 'TIME', 1001):
            with self.assertRaises(RuntimeError):
                self.module.set_last_activity(self.user)
        self.assertNotIn('gdo:test:user:presence:42:written', self.data)
        self.assertNotIn('gdo:test:user:presence:42:lock', self.data)

    def test_redis_failure_falls_back_to_database(self):
        self.redis.set.side_effect = RedisError('unavailable')
        with patch.object(Cache, 'RCACHE', self.redis), \
             patch.object(Application, 'config', return_value='test'), \
             patch.object(self.module, 'cfg_activity_accuracy', return_value=300), \
             patch('gdo.user.module_user.Logger.exception'), \
             patch('gdo.user.module_user.Time.get_date', return_value='exact'):
            self.module.set_last_activity(self.user)
        self.user.save_setting.assert_called_once_with('last_activity', 'exact')

    def test_online_combines_connector_and_recent_activity(self):
        user = GDO_User()
        server = Mock()
        server.is_user_online.return_value = False
        provider = Mock()
        provider.instance.return_value.is_recently_active.return_value = True
        with patch.object(GDO_User, 'get_server', return_value=server), \
             patch.object(Application, 'get_module_user', return_value=provider):
            self.assertTrue(user.is_online())
            provider.instance.return_value.is_recently_active.return_value = False
            self.assertFalse(user.is_online())
            server.is_user_online.return_value = True
            self.assertTrue(user.is_online())
