from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from gdo.base.Method import Method
from gdo.date.Time import Time


class time(Method):
    @classmethod
    def gdo_trig(cls):
        return 'time'

    def gdo_execute(self):
        user = self._env_user
        zone = user.get_setting_value('timezone')
        if not zone:
            return self.err('date_timezone_unavailable')
        name = zone.gdo_val('tz_name')
        try:
            tz = ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            tz = timezone(zone.get_delta(), name)
        now = datetime.now(timezone.utc)
        local = now.astimezone(tz)
        formatted = Time.display_datetime_iso(user.get_lang_iso() or 'en', local, 'short')
        return self.reply('date_time_result', (formatted, name, local.strftime('%z'), int(now.timestamp())))
