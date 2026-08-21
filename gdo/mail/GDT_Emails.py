from gdo.core.GDT_String import GDT_String
from gdo.mail.GDT_Email import GDT_Email


class GDT_Emails(GDT_String):
    """A comma-separated list of individually validated email addresses."""

    def __init__(self, name: str):
        super().__init__(name)
        self.ascii().maxlen(1024).icon('email')
        self._input_type = 'email'

    def validate(self, val: str | None) -> bool:
        if not super().validate(val):
            return False
        if not val:
            return True
        for email in (item.strip() for item in val.split(',')):
            if not email or not GDT_Email('email').validate(email):
                return self.error('err_emails_invalid', (email,))
        return True
