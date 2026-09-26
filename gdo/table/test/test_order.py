import unittest
from gdotest.TestUtil import GDOTestCase

from gdo.table.GDT_Order import GDT_Order


class OrderTest(GDOTestCase):

    def test_explicit_direction(self):
        order = GDT_Order('o').initial(['file_name ASC'])
        self.assertEqual({'file_name': 'ASC'}, order.get_order_dict())

    def test_missing_direction_defaults_to_def(self):
        order = GDT_Order('o').initial(['file_name'])
        self.assertEqual({'file_name': 'DEF'}, order.get_order_dict())
