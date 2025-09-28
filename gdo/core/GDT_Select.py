from gdo.base.Trans import t
from gdo.base.Util import Arrays
from gdo.core.GDT_ComboBox import GDT_ComboBox
from gdo.core.GDT_Template import tpl


class GDT_Select(GDT_ComboBox):

    def gdo_choices(self) -> dict:
        return {}

    def init_choices(self):
        if not hasattr(self, '_choices'):
            self._choices = {}
        else:
            return self._choices
        if not self.is_not_null():
            self._choices[''] = t('please_choose')
        self._choices.update(self.gdo_choices())
        return self._choices

    def validate(self, val: str|None) -> bool:
        if val is None:
            return super().validate(val)
        if (value := self.to_value(val)) is not None:
            self.value(value)
            return True
        return self.error_invalid_choice()

    def error_invalid_choice(self):
        suggestions = self.render_suggestion()
        if suggestions == '':
            return self.error('err_invalid_choice_no_suggestions')
        else:
            return self.error('err_invalid_choice', (suggestions,))

    def to_val(self, value) -> str:
        return Arrays.dict_index(self.init_choices(), value)

    def to_value(self, val: str):
        self.init_choices()
        matches = []
        val = val.lower()
        for k, v in self._choices.items():
            if k.lower().startswith(val) or (type(v) == str and v.lower().startswith(val)):
                matches.append(v)
            if k.lower() == val or (type(v) == str and v.lower() == val):
                return v
        if len(matches) == 1: return matches[0]
        matches = []
        for k, v in self._choices.items():
            if val in k.lower() or (type(v) == str and val in v.lower()):
                matches.append(v)
        if len(matches) == 1: return matches[0]
        return None

    ##########
    # Render #
    ##########

    def html_selected(self, key: str):
        if key == self.get_val():
            return ' selected="selected"'
        return self.EMPTY_STR

    def render_suggestion(self) -> str:
        self.init_choices()
        keys = self._choices.keys()
        examples = list(keys)[0:5]
        if len(keys) > 5:
            examples.append('...')
        return ", ".join(examples)

    def render_form(self):
        return tpl('core', 'form_select.html', {"field": self})
