from gdo.base.GDO_Module import GDO_Module


class module_install(GDO_Module):

    def is_installable(self) -> bool:
        return False
