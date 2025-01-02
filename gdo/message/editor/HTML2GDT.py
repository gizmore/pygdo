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
from gdo.ui.GDT_Divider import GDT_Divider


class HTML2GDT(HTMLParser):
    HTML_TO_GDT = {
        'p': GDT_Paragraph,
        'b': GDT_Bold,
        'i': GDT_Italic,
        'stroke': GDT_Stroke,
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
        super().__init__()
        self.root = GDT_Container()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        gdt_type = self.HTML_TO_GDT.get(tag, GDT_Container)
        node = gdt_type()
        for key, value in attrs:
            node.attr(key, value)
        self.stack[-1].add_field(node)
        self.stack.append(node)

    def handle_endtag(self, tag):
        self.stack.pop()

    def handle_data(self, data: str):
        if data :=data.strip():
            text_node = GDT_HTML().text(data)
            self.stack[-1].add_field(text_node)

    def parse(self, html) -> GDT:
        self.feed(html)
        return self.root
