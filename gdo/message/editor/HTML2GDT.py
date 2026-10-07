from html.parser import HTMLParser

from gdo.base.GDT import GDT
from gdo.core.GDT_Container import GDT_Container
from gdo.core.WithFields import WithFields
from gdo.message.GDT_Anchor import GDT_Anchor
from gdo.message.GDT_Bold import GDT_Bold
from gdo.message.GDT_Div import GDT_Div
from gdo.message.GDT_H1 import GDT_H1
from gdo.message.GDT_H2 import GDT_H2
from gdo.message.GDT_H3 import GDT_H3
from gdo.message.GDT_H4 import GDT_H4
from gdo.message.GDT_H5 import GDT_H5
from gdo.message.GDT_H6 import GDT_H6
from gdo.message.GDT_HTML import GDT_HTML
from gdo.message.GDT_Italic import GDT_Italic
from gdo.message.GDT_Newline import GDT_Newline
from gdo.message.GDT_Paragraph import GDT_Paragraph
from gdo.message.GDT_Span import GDT_Span
from gdo.message.GDT_Stroke import GDT_Stroke
from gdo.message.GDT_Underline import GDT_Underline
from gdo.message.GDT_PRE import GDT_PRE
from gdo.ui.GDT_Divider import GDT_Divider


class GDT_HTMLRoot(GDT_Container):
    """Parser root that preserves neighbouring text-node whitespace."""

    def render_fields(self, mode=None) -> str:
        from gdo.base.Render import Mode
        mode = mode or Mode.render_html
        return ''.join(gdt.render(mode) for gdt in self._fields)


class HTML2GDT(HTMLParser):
    HTML_TO_GDT = {
        'p': GDT_Paragraph,
        'b': GDT_Bold,
        'strong': GDT_Bold,
        'i': GDT_Italic,
        'em': GDT_Italic,
        'u': GDT_Underline,
        's': GDT_Stroke,
        'strike': GDT_Stroke,
        'del': GDT_Stroke,
        'pre': GDT_PRE,
        'text': GDT_HTML,
        'h1': GDT_H1,
        'h2': GDT_H2,
        'h3': GDT_H3,
        'h4': GDT_H4,
        'h5': GDT_H5,
        'h6': GDT_H6,
        'a': GDT_Anchor,
        'div': GDT_Div,
        'hr': GDT_Divider,
        'span': GDT_Span,
        'br': GDT_Newline,
    }

    root: GDT_Container
    stack: list[GDT|WithFields]

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = GDT_HTMLRoot()
        self.stack = [self.root]
        self.tags = [None]

    def handle_starttag(self, tag, attrs):
        gdt_type = self.HTML_TO_GDT.get(tag, GDT_Container)
        node = gdt_type()
        for key, value in attrs:
            node.attr(key, value)
        self.stack[-1].add_field(node)
        if tag not in ('br', 'hr'):
            self.stack.append(node)
            self.tags.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ('br', 'hr'):
            return
        if len(self.stack) > 1 and self.tags[-1] == tag:
            self.stack.pop()
            self.tags.pop()

    def handle_data(self, data: str):
        if data:
            text_node = GDT_HTML().text(data)
            self.stack[-1].add_field(text_node)

    def parse(self, html) -> GDT:
        self.feed(html)
        return self.root
