from gdo.core.GDO import GDO
from gdo.core.GDT import GDT


class GDT_Field(GDT):

    _name: str
    _gdo: GDO
    _not_null: bool
    _erraw: str
    _errkey: str
    _errargs: list
    _val: str
    _initial: str
    _converted: bool
    _primary: bool
    _unique: bool

    def __init__(self, name):
        self._name = name
        self._not_null = False
        self._val = ''
        self._initial = ''
        self._primary = False
        self._value = None
        self._converted = False


    def get_name(self):
        return self._name

    def gdo(self, gdo: GDO):
        self._gdo = gdo
        self._val = gdo.get(self._name)
        return self

    def initial(self, val: str):
        self._initial = val
        return self

    def is_primary(self):
        return self._primary

    def primary(self, primary=True):
        self._primary = primary
        return self

    def unique(self, unique=True):
        self._unique = unique
        return self

    def gdo_column_define_null(self) -> str:
        if self._not_null:
            return 'NOT NULL'
        return ''

    def gdo_column_define_default(self) -> str:
        if self._initial != '':
            return "DEFAULT " + self.quote(self._initial)
        return ''

    def not_null(self, not_null=True):
        self._not_null = not_null
        return self

    def error(self, errkey, errargs=None):
        if errargs is None:
            errargs = []
        self._errkey = errkey
        self._errargs = errargs
        return False

    def validate(self, value):
        if value is None:
            if self._not_null:
                return self.error('err_not_null')

        if self._unique and not self.validate_unique(value):
            return False

        return True

    def validate_unique(self, value):
        self._gdo.table().select()

