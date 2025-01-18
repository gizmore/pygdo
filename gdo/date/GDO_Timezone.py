from datetime import timedelta

from gdo.base.GDO import GDO


class GDO_Timezone(GDO):

    ##########
    # Static #
    ##########

    @classmethod
    def get_by_name(cls, timezone_name):
        return cls.table().get_by('tz_name', timezone_name)

    #######
    # GDO #
    #######
    
    def __init__(self):
        super().__init__()

    def gdo_columns(self):
        from gdo.core.GDT_AutoInc import GDT_AutoInc
        from gdo.core.GDT_Int import GDT_Int
        from gdo.core.GDT_Name import GDT_Name
        return [
            GDT_AutoInc('tz_id'),
            GDT_Name('tz_name').unique(),
            GDT_Int('tz_offset').not_null().initial('0')
        ]

    def gdo_persistent(self) -> bool:
        return True

    ##########
    # Getter #
    ##########
    def get_offset(self) -> int:
        return self.gdo_value('tz_offset')

    def get_delta(self) -> timedelta:
        return timedelta(seconds=self.get_offset())

