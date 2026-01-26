from gdo.core.GDT_String import GDT_String


class GDT_SearchTerm(GDT_String):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('search')
        self.label('search_term')
