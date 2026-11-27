from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from gdo.base.Method import Method
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Timezone import GDT_Timezone
from gdo.date.Time import Time


class time(Method):
    @classmethod
    def gdo_trig(cls):
        return 'time'

    def gdo_parameters(self):
        return [GDT_User('user').positional(), GDT_Timezone('timezone')]

    def gdo_execute(self):
        user = self.param_value('user') or self._env_user
        zone = self.param_value('timezone') or user.get_setting_value('timezone')
        if not zone:
            return self.err('date_timezone_unavailable')
        name = zone.gdo_val('tz_name')
        try:
            tz = ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            tz = timezone(zone.get_delta(), name)
        now = datetime.now(timezone.utc)
        local = now.astimezone(tz)
        language = self._env_user.get_lang_iso() or 'en'
        formatted = Time.display_datetime_iso(language, local, 'short')
        if name.casefold() in ('utc', 'etc/utc', 'etc/uct', 'uct', 'universal', 'zulu'):
            return self.reply('date_time_result', (formatted, name, local.strftime('%z'), int(now.timestamp())))
        utc = Time.display_datetime_iso(language, now, 'short')
        return self.reply('date_time_with_utc', (formatted, name, local.strftime('%z'), utc, int(now.timestamp())))
