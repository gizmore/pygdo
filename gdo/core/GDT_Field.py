from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.ui.WithIcon import WithIcon
from gdo.ui.WithTooltip import WithTooltip


class GDT_Field(WithTooltip, WithIcon, GDT):

    _name: str
    _gdo: GDO
    _not_null: bool
    _val: str
    _initial: str
    _converted: bool
    _primary: bool
    _unique: bool

    def __init__(self, name):
        super().__init__()
        self._name = name
        self._not_null = False
        self._val = ''
        self._initial = ''
        self._primary = False
        self._value = None
        self._converted = False

    def get_name(self):
        return self._name

    def get_val(self):
        if not self._val:
            return None
        return str(self._val)

    def get_value(self):
        if not self._converted:
            self._value = self.to_value(self.get_val())
            self._converted = True
        return self._value

    def val(self, val: str):
        self._val = val
        self._converted = False
        delattr(self, '_value')
        return self

    def value(self, value):
        self._converted = True
        self._value = value
        self._val = self.to_val(value)
        return self

    def gdo(self, gdo: GDO):
        self._gdo = gdo
        self._val = gdo.gdo_val(self._name)
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

