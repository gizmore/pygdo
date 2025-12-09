from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.base.WithName import WithName
from gdo.core.GDT_Template import GDT_Template


class GDT_TreeView(WithName, GDT):

    _query: Query|None
    _parent_col: str|None
    _roots: list|None
    _children: dict|None
    

    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._query = None
        self._parent_col = None
        self._roots = None
        self._children = None

    def query(self, query: Query) -> GDT_TreeView:
        self._query = query
        return self

    def parent_col(self, parent_col: str):
        self._parent_col = parent_col
        return self

    def render(self, mode: Mode = Mode.render_html) -> str:
        return GDT_Template().template('ui', 'treeview.html', {'field': self, 'query': self._query}).render_html()

    def _build_tree(self):
        """Build roots + child map from the flat query result."""
        by_parent = {}
        roots = []

        for row in self._query.exec():
            parent_id = row.gdo_val(self._parent_col)
            if parent_id:
                by_parent[parent_id].append(row)
            else:
                roots.append(row)

        self._roots = roots
        self._children = by_parent

    def roots(self):
        if self._roots is None:
            self._build_tree()
        return self._roots

    def children(self, node):
        if self._children is None:
            self._build_tree()
        node_id = node.get_id()
        return self._children.get(node_id, [])
