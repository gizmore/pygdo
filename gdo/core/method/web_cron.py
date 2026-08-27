from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.Cronjob import Cronjob


class web_cron(Method):

    def gdo_user_permission(self) -> str | None:
        return 'cronjob'

    def gdo_execute(self) -> GDT:
        executed = Cronjob.run(True)
        return self.reply('msg_core_web_cron_done', (len(executed), ', '.join(executed)))
    
