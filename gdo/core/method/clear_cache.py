from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core import module_core


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
        if mc := module_core.instance():
            if mc.is_persisted():
                mc.save_config_val('av', str(int(mc.cfg_asset_version()) + 1))
        await Application.EVENTS.publish('clear_cache')
        Cache.clear()
        return self.empty('msg_cache_cleared')
