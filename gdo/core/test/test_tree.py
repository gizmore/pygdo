import os

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Tree import GDT_Tree
from gdotest.TestUtil import GDOTestCase


class TreeNode(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('node_id'),
            GDT_Tree('node').not_null(),
        ]


class TreeTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        Application.init_cli()

    def test_tree_expands_to_left_and_right_columns(self):
        columns = TreeNode.table().columns()

        self.assertIn('node', columns)
        self.assertIn('node_left', columns)
        self.assertIn('node_right', columns)
        self.assertTrue(columns['node_left'].is_not_null())
        self.assertTrue(columns['node_right'].is_not_null())

    def test_tree_reads_and_sets_bounds_as_a_pair(self):
        node = TreeNode.blank({'node_left': '1', 'node_right': '8'})
        tree = node.column('node')

        self.assertEqual((1, 8), tree.get_value())
        tree.set((2, 7))
        self.assertEqual('2', node.gdo_val('node_left'))
        self.assertEqual('7', node.gdo_val('node_right'))
        self.assertEqual((2, 7), tree.get_value())
