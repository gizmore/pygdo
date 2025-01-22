from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.date.Time import Time


class stats(Method):

    def gdo_execute(self) -> GDT:
        app = Application
        return self.reply('msg_stats', (
            Time.human_duration(app.runtime()),
            (app.DB_READS + app.DB_WRITES) / app.runtime(),
        ))
