from gdo.base.Trans import t
from gdo.base.Util import Arrays
from gdo.core.GDT_ComboBox import GDT_ComboBox
from gdo.core.GDT_Template import tpl


class GDT_Select(GDT_ComboBox):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {}

    def init_choices(self):
        if not hasattr(self, '_choices'):
            self._choices = {}
        else:
            return self._choices
        if not self.is_not_null():
            self._choices['0'] = t('please_choose')
        self._choices.update(self.gdo_choices())
        return self._choices

    def validate(self, val: str | None, value: any) -> bool:
        if value is None:
            return super().validate(val, value)
        choices = self.init_choices()
        if val not in choices.keys():
            return self.error_invalid_choice()
        return True

    def error_invalid_choice(self):
        suggestions = self.render_suggestion()
        if suggestions == '':
            return self.error('err_invalid_choice_no_suggestions')
        else:
            return self.error('err_invalid_choice', (suggestions,))

    def to_val(self, value) -> str:
        return Arrays.dict_index(self.init_choices(), value)

    def to_value(self, val: str):
        if val is None:
            return None
        self.init_choices()
        return self._choices[val]

    ##########
    # Render #
    ##########

    def html_selected(self, key: str):
        if key == self.get_val():
            return ' selected="selected"'
        return ''

    def render_suggestion(self) -> str:
        self.init_choices()
        keys = self._choices.keys()
        examples = list(keys)[0:5]
        if len(keys) > 5:
            examples.append('...')
        return ", ".join(examples)

    def render_form(self):
        return tpl('core', 'form_select.html', {"field": self})
