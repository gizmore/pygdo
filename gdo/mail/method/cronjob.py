from gdo.base.GDT import GDT
from gdo.core.MethodCronjob import MethodCronjob
from gdo.mail.GDO_Mail import GDO_Mail


class cronjob(MethodCronjob):

    def gdo_execute(self) -> GDT:
        mail = GDO_Mail.table().select().where('mail_sent IS NULL').first().exec().fetch_object()
