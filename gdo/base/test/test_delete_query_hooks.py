import sqlite3
import unittest
from contextlib import closing
from unittest.mock import MagicMock, patch

from gdo.base.GDO import GDO
from gdo.base.Cache import Cache
from gdo.base.Application import Application
from gdo.base.Query import Query, Type
from gdo.date.GDT_Deleted import GDT_Deleted


class DeleteQueryHookTest(unittest.TestCase):
    def test_delete_runs_query_hooks_in_order(self):
        obj = MagicMock()
        obj.is_persisted.return_value = True
        obj.gdo_can_persist.return_value = True
        obj.gdo_cached.return_value = False
        obj.get_pk_columns.return_value = []
        field = MagicMock()
        obj.columns.return_value = {'field': field}
        query = obj.delete_query.return_value
        query.where.return_value = query
        events = []
        obj.before_delete.side_effect = lambda: events.append('before')
        field.gdo_before_delete_query.side_effect = lambda *args: events.append('field-before')
        obj.gdo_before_delete_query.side_effect = lambda *args: events.append('object-before')
        query.exec.side_effect = lambda: events.append('execute') or 'result'
        obj.gdo_after_delete_query.side_effect = lambda *args: events.append('object-after')
        field.gdo_after_delete_query.side_effect = lambda *args: events.append('field-after')
        obj.after_delete.side_effect = lambda: events.append('after')

        GDO.delete(obj)

        self.assertEqual(['before', 'field-before', 'object-before', 'execute',
                          'object-after', 'field-after', 'after'], events)
        field.gdo_after_delete_query.assert_called_once_with(obj, query, 'result')

    def test_deleted_gdt_changes_query_to_update(self):
        field = GDT_Deleted.__new__(GDT_Deleted)
        obj = MagicMock()
        obj.dirty_vals.return_value = {'deleted_at': '2026-01-01', 'deleted_by': '1'}
        query = Query().table('example').type(Type.DELETE).where('id=1')
        field.gdo_before_delete_query(obj, query)
        self.assertTrue(query.is_update())
        self.assertEqual(obj.dirty_vals.return_value, query._vals)
        self.assertIn('id=1', query._where)

    def test_failed_query_does_not_run_after_hooks(self):
        obj = MagicMock()
        obj.is_persisted.return_value = True
        obj.gdo_can_persist.return_value = True
        field = MagicMock()
        obj.columns.return_value = {'field': field}
        query = obj.delete_query.return_value
        query.where.return_value = query
        query.exec.side_effect = RuntimeError('database unavailable')
        with self.assertRaisesRegex(RuntimeError, 'database unavailable'):
            GDO.delete(obj)
        obj.gdo_after_delete_query.assert_not_called()
        field.gdo_after_delete_query.assert_not_called()
        obj.after_delete.assert_not_called()

    def test_soft_and_hard_queries_against_database(self):
        with closing(sqlite3.connect(':memory:')) as db:
            db.execute('CREATE TABLE example (id INTEGER PRIMARY KEY, deleted_at TEXT, deleted_by TEXT)')
            db.executemany('INSERT INTO example (id) VALUES (?)', [(1,), (2,)])
            field = GDT_Deleted.__new__(GDT_Deleted)
            obj = MagicMock()
            obj.dirty_vals.return_value = {'deleted_at': '2026-01-01', 'deleted_by': '1'}
            soft = Query().table('example').type(Type.DELETE).where('id=1')
            field.gdo_before_delete_query(obj, soft)
            db.execute(soft.build_query())
            hard = Query().table('example').type(Type.DELETE).where('id=2')
            db.execute(hard.build_query())
            self.assertEqual([(1, '2026-01-01', '1')], db.execute(
                'SELECT id, deleted_at, deleted_by FROM example').fetchall())

    def test_gdo_delete_runs_deleted_field_against_database(self):
        with closing(sqlite3.connect(':memory:')) as db:
            db.execute('CREATE TABLE example (id INTEGER PRIMARY KEY, deleted_at TEXT)')
            db.execute('INSERT INTO example (id) VALUES (1)')
            field = GDT_Deleted.__new__(GDT_Deleted)
            field._name = 'deleted_at'
            obj = MagicMock()
            obj.is_persisted.return_value = True
            obj.gdo_can_persist.return_value = True
            obj.gdo_cached.return_value = False
            obj.get_pk_columns.return_value = []
            obj.pk_where.return_value = 'id=1'
            obj.columns.return_value = {'deleted_at': field}
            obj.delete_query.return_value = Query().table('example').type(Type.DELETE)
            values = {}
            obj.set_val.side_effect = lambda name, value: values.update({name: value})
            obj.dirty_vals.side_effect = lambda: values.copy()
            obj.before_delete.side_effect = lambda: field.gdo_before_delete(obj)
            with patch.object(Query, 'exec', autospec=True, side_effect=lambda query: db.execute(query.build_query())):
                GDO.delete(obj)
            row = db.execute('SELECT id, deleted_at FROM example').fetchone()
            self.assertEqual(1, row[0])
            self.assertTrue(row[1])

    def test_soft_delete_invalidates_existing_cached_row(self):
        obj = MagicMock()
        obj.is_persisted.return_value = True
        obj.gdo_can_persist.return_value = True
        obj.gdo_cached.return_value = True
        obj.gdo_table_name.return_value = 'example'
        obj.pk_where.return_value = 'id=1'
        key = MagicMock()
        key.get_name.return_value = 'id'
        key.get_val.return_value = '1'
        obj.get_pk_columns.return_value = [key]
        field = GDT_Deleted.__new__(GDT_Deleted)
        field._name = 'deleted_at'
        obj.columns.return_value = {'deleted_at': field}
        obj.before_delete.side_effect = lambda: field.gdo_before_delete(obj)
        obj.dirty_vals.return_value = {'deleted_at': '2026-01-01'}
        obj.delete_query.return_value = Query().table('example').type(Type.DELETE)
        with patch.object(Cache, 'OCACHE', {'example': {'1': obj}}, create=True), \
             patch.object(Cache, 'remove') as remove, \
             patch.object(Cache, 'get', return_value=None), \
             patch.object(Application, 'transaction_depth', return_value=0), \
             patch.object(Query, 'exec', return_value=MagicMock()):
            GDO.delete(obj)
            self.assertNotIn('1', Cache.OCACHE['example'])
            remove.assert_called_once_with('example', '1')


if __name__ == '__main__':
    unittest.main()
