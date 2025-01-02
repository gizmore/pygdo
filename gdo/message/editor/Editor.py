import functools

from purifier.purifier import HTMLPurifier

from gdo.base.Exceptions import GDOException
from gdo.base.GDT import GDT
from gdo.message.editor.HTML2GDT import HTML2GDT


class Editor:

    @classmethod
    def get_name(cls) -> str:
        raise GDOException(f"{cls.__name__} has to implement get_name()")

    @classmethod
    def to_html(cls, input: str) -> str:
        return cls.filter_html(input)

    @classmethod
    def filter_html(cls, html: str) -> str:
        purifier = cls.get_purifier()
        return purifier.feed(html)

    @classmethod
    @functools.cache
    def get_purifier(cls) -> HTMLPurifier:
        return HTMLPurifier({
            'div': ['style'],
            'span': ['style'],
            'a': ['href', 'style'],
            'p': [],
            'b': [],
            'i': [],
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': [],
        })

    @classmethod
    def parse_tree(cls, html: str) -> GDT:
        return HTML2GDT().parse(html)
