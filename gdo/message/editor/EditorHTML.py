from gdo.message.editor.Editor import Editor


class EditorHTML(Editor):

    @classmethod
    def get_name(cls) -> str:
        return 'html'

    @classmethod
    def to_html(cls, input: str) -> str:
        return super().to_html(input)
