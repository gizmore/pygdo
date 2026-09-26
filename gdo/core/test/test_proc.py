import unittest
from gdotest.TestUtil import GDOTestCase
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Render import Mode
from gdo.core.GDO_Process import GDO_Process
from gdo.core.method.proc import proc


class ProcTest(GDOTestCase):

    def setUp(self):
        Application.mode(Mode.render_cli)
        if not hasattr(Cache, 'TCACHE'):
            Cache.init()

    @patch('gdo.core.method.proc.subprocess.run')
    def test_read_processes_uses_fixed_ps_command(self, run):
        run.return_value = MagicMock(stdout=' 12 25.0 1.0 worker\n 7 70.5 2.5 python\n')
        rows = proc.read_processes()
        self.assertEqual(['worker', 'python'], [row.get_name() for row in rows])
        self.assertEqual(70.5, rows[1].gdo_value('proc_load'))
        self.assertEqual(['ps', '-eo', 'pid=,pcpu=,pmem=,comm='], run.call_args.args[0])

    def test_default_load_filter_is_at_least_25_percent(self):
        method = proc()
        method.parameters()
        self.assertEqual(['25-'], method.table_filter_field().get_val()['proc_load'])
        self.assertTrue(proc.matches_load(25.0, '25-'))
        self.assertTrue(proc.matches_load(70.5, '25-'))
        self.assertFalse(proc.matches_load(24.9, '25-'))

    @patch.object(proc, 'gdo_paginate_size', return_value=10)
    @patch.object(proc, 'read_processes')
    def test_default_filter_excludes_processes_below_25_percent(self, read_processes, _):
        read_processes.return_value = [
            GDO_Process.blank({'proc_pid': '1', 'proc_load': '24.9', 'proc_memory': '1', 'proc_command': 'idle'}),
            GDO_Process.blank({'proc_pid': '2', 'proc_load': '25', 'proc_memory': '1', 'proc_command': 'worker'}),
            GDO_Process.blank({'proc_pid': '3', 'proc_load': '70', 'proc_memory': '1', 'proc_command': 'busy'}),
        ]
        method = proc()
        method.parameters()
        self.assertEqual(['busy', 'worker'], [row.get_name() for row in method.get_table_result()])

    def test_is_owner_only(self):
        self.assertEqual('owner', proc().gdo_user_permission())
