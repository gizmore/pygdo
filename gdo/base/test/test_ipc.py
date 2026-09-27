import unittest
from gdotest.TestUtil import GDOTestCase
from unittest.mock import AsyncMock, patch

import msgspec

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Database import Database
from gdo.base.IPC import IPC


class IPCWakeupTest(GDOTestCase):
    def setUp(self):
        self.old_pid = IPC.PID
        self.old_next_check = IPC.DOG_NEXT_CHECK
        self.old_time = Application.TIME
        self.old_ipc_ts = Application.IPC_TS
        self.old_redis = Cache.RCACHE
        IPC.PID = 123
        IPC.DOG_NEXT_CHECK = 0
        Application.TIME = 100.0
        Application.IPC_TS = 0.0

    def tearDown(self):
        IPC.PID = self.old_pid
        IPC.DOG_NEXT_CHECK = self.old_next_check
        Application.TIME = self.old_time
        Application.IPC_TS = self.old_ipc_ts
        Cache.RCACHE = self.old_redis

    class FakeRedis:
        def __init__(self):
            self.queue = []

        def rpush(self, key, value):
            self.queue.append((key, value))

        def lpop(self, key):
            if self.queue and self.queue[0][0] == key:
                return self.queue.pop(0)[1]
            return None

    @patch('gdo.base.IPC.GDO_Event.to_dog')
    @patch('gdo.base.IPC.os.kill')
    def test_redis_mode_queues_without_database_or_signal(self, kill, to_dog):
        redis = self.FakeRedis()
        Cache.RCACHE = redis
        args = ('gdo_session', '1', {'sess_data': b'{"captcha":"UAASP"}'})
        with patch.object(IPC, 'cfg_dog_mode', return_value='redis'):
            IPC.send_to_dog('base.ipc_gdo', args)

        self.assertEqual(1, len(redis.queue))
        event = msgspec.json.decode(redis.queue[0][1])
        self.assertEqual('base.ipc_gdo', event['name'])
        kill.assert_not_called()
        to_dog.assert_not_called()

    async def test_dog_drains_the_redis_queue_at_most_once_per_second(self):
        redis = self.FakeRedis()
        redis.rpush(IPC.REDIS_QUEUE, msgspec.json.encode({'name': 'base.ipc_gdo', 'args': ['gdo_session', '1', {}]}))
        Cache.RCACHE = redis
        with patch.object(IPC, 'cfg_dog_mode', return_value='redis'), \
                patch.object(IPC, 'execute_dog_event', AsyncMock()) as execute:
            await IPC.dog_check_for_ipc()
            await IPC.dog_check_for_ipc()

        execute.assert_awaited_once()

    def test_ipc_waits_for_a_transaction_commit(self):
        db = Database('', '', '', '')
        db.link = self.FakeLink()
        db.link.in_transaction = True
        with (
            patch.object(Application, 'db', return_value=db),
            patch.object(IPC, 'send_now') as send_now,
        ):
            IPC.send('base.ipc_gdo', ('gdo_user', '1', {}))
            send_now.assert_not_called()
            db.commit()
        send_now.assert_called_once_with('base.ipc_gdo', ('gdo_user', '1', {}))

    def test_ipc_discards_a_rolled_back_transaction(self):
        db = Database('', '', '', '')
        db.link = self.FakeLink()
        db.link.in_transaction = True
        with (
            patch.object(Application, 'db', return_value=db),
            patch.object(IPC, 'send_now') as send_now,
        ):
            IPC.send('base.ipc_gdo', ('gdo_user', '1', {}))
            db.rollback()
        send_now.assert_not_called()

    def test_ipc_waits_for_the_outermost_nested_commit(self):
        db = Database('', '', '', '')
        db.link = self.FakeLink()
        with (
            patch.object(Application, 'db', return_value=db),
            patch.object(IPC, 'send_now') as send_now,
        ):
            db.begin()
            IPC.send('base.ipc_gdo', ('gdo_user', '1', {}))
            db.begin()
            db.commit()
            send_now.assert_not_called()
            db.commit()
        self.assertEqual(1, db.link.commits)
        send_now.assert_called_once_with('base.ipc_gdo', ('gdo_user', '1', {}))

    class FakeLink:
        in_transaction = False

        def __init__(self):
            self.commits = 0

        def close(self):
            pass

        def start_transaction(self):
            self.in_transaction = True

        def commit(self):
            self.in_transaction = False
            self.commits += 1

        def rollback(self):
            self.in_transaction = False


if __name__ == '__main__':
    unittest.main()
