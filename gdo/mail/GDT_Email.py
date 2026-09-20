import random

from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.core.GDT_String import GDT_String


class GDT_Email(GDT_String):

    _obfuscate: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.ascii().maxlen(96).case_i()
        # Account mail must remain portable across ordinary SMTP relays.
        # SMTPUTF8 is optional end-to-end, so reject non-ASCII directly in
        # the field pattern instead of accepting an address that may fail at
        # delivery time.
        self.pattern(r"^(?=[\x00-\x7F]+$)[^@\s]+@[^@\s]+$")
        self.icon('email')
        self._obfuscate = False
        self._input_type = "email"

    def obfuscate(self, obfuscate: bool = True):
        self._obfuscate = obfuscate
        return self

    def render_val(self) -> str:
        return self.render_obfuscated() if self._obfuscate else self.get_val()

    def render_obfuscated(self) -> str:
        val = self.get_val() or ''
        if not val:
            return Render.italic(t('none'))
        dot_variants = (" dot ", " [dot] ", " _dot_ ")
        at_variants = (" at ", " [at] ", " _at_ ")
        out = []
        for ch in val:
            if ch == '.':
                out.append(random.choice(dot_variants))
            elif ch == '@':
                out.append(random.choice(at_variants))
            else:
                out.append(ch)
        return ''.join(out)
