from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.core.GDT_Template import GDT_Template
from gdo.core.WithLabel import WithLabel
from gdo.ui.GDT_Bar import GDT_Bar
from typing import Iterator, Tuple

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.table.MethodTable import MethodTable


class GDT_PageMenu(WithLabel, GDT_Bar):

    _num_items: int
    _page_num: int
    _ipp: int
    _method: MethodTable

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.label('page_menu')

    def paginate(self, method: MethodTable):
        self._num_items = max(0, int(method.get_num_results()))
        self._page_num = max(1, int(method.get_page_num()))
        self._ipp = max(1, int(method.gdo_paginate_size()))
        self._method = method
        return self

    def num_pages(self) -> int:
        if self._num_items <= 0:
            return 1
        return ((self._num_items - 1) // self._ipp) + 1

    def _href_with(self, base_href: str, key: str, val: int) -> str:
        parts = urlsplit(base_href)
        q = dict(parse_qsl(parts.query, keep_blank_values=True))
        if val <= 1:
            q.pop(key, None)  # keep URLs clean: no &p=1
        else:
            q[key] = str(val)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q, doseq=True), parts.fragment))

    def page_items(self) -> Iterator[Tuple[int, bool, str]]:
        base_href = Application.current_href()
        paginator = self._method.table_paginate_field().get_name()
        run = max(0, int(self._method.get_page_menu_run_len()))

        last = self.num_pages()
        cur = min(max(1, int(self._page_num)), last)

        def href(p: int) -> str:
            return self._href_with(base_href, paginator, p)

        if last <= (2 * run + 5):
            for p in range(1, last + 1):
                yield p, (p == cur), href(p)
            return

        left = cur - run
        right = cur + run

        if left < 2:
            right += (2 - left)
            left = 2
        if right > last - 1:
            left -= (right - (last - 1))
            right = last - 1
            if left < 2:
                left = 2

        yield 1, (cur == 1), href(1)

        if left > 2:
            yield -1, False, ""

        for p in range(left, right + 1):
            yield p, (p == cur), href(p)

        if right < last - 1:
            yield -1, False, ""

        yield last, (cur == last), href(last)


    def render_html(self, mode: Mode = Mode.render_html):
        return GDT_Template().template('table', 'page_menu.html', {'field': self, 'mode': mode}).render_html(mode)
