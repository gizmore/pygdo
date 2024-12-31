from html.parser import HTMLParser

from gdo.base.GDT import GDT
from gdo.core.GDT_Container import GDT_Container
from gdo.message.GDT_Bold import GDT_Bold
from gdo.message.GDT_Div import GDT_Div
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
        'div': GDT_Div,
        'hr': GDT_Divider,
        'span': GDT_Span,
        'br': GDT_Newline,
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.root = None

    def handle_starttag(self, tag, attrs):
        gdt_type = self.HTML_TO_GDT.get(tag, GDT_Container)
        node = gdt_type()
        if self.stack:
            self.stack[-1].add_field(node)
        else:
            self.root = node
        self.stack.append(node)

    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str):
        if data.strip():  # Ignore whitespace
            text_node = GDT_HTML().text(data.strip())
            if not self.stack:
                self.root = GDT_Container()
                self.stack.append(self.root)
            self.stack[-1].add_field(text_node)

    def parse(self, html) -> GDT:
        self.feed(html)
        return self.root
