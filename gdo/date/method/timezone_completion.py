from gdo.core.MethodCompletion import MethodCompletion
from gdo.date.GDO_Timezone import GDO_Timezone


class timezone_completion(MethodCompletion):

    def gdo_completion_items(self) -> list[dict[str, str]]:
        query = self.get_query()
        timezones = GDO_Timezone.table().select().where(
            f"tz_name LIKE '%{GDO_Timezone.escape(query)}%'"
        ).limit(10).exec().fetch_all()
        return [
            {
                'id': timezone.get_id(),
                'var': timezone.gdo_val('tz_name'),
                'display_var': timezone.render_name(),
            }
            for timezone in timezones
        ]
