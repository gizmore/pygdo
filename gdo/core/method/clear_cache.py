from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method


class clear_cache(Method):
    """
    Clear all caches. Uses an Event to allow others to clean up as well
    """

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    @classmethod
    def gdo_trigger(cls) -> str:
        return "cc"

    async def gdo_execute(self) -> GDT:
        Cache.clear()
        await Application.EVENTS.publish('clear_cache')
        return self.reply('msg_cache_cleared')
