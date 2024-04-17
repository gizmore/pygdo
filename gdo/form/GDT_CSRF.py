from gdo.form.GDT_Hidden import GDT_Hidden


class GDT_CSRF(GDT_Hidden):

    def __init__(self, name='csrf'):
        super().__init__(name)

