from gdo.base.GDT import GDT
from gdo.base.WithError import WithError


class GDT_Validator(WithError, GDT):

    def __init__(self):
        super().__init__()
