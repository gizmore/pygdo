from gdo.admin.GDT_Module import GDT_Module
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_String import GDT_String


class ipc_modconf(Method):
    """
    Update a module config.
    """

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Module('module').not_null(),
            GDT_Name('key').not_null(),
            GDT_String('value').not_null(),
        ]

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_execute(self) -> GDT:
        """
        Only update the module config.
        """
        module = self.get_module()
        key = self.param_val('key')
        val = self.param_val('value')
        gdt = module._module_config.get(key)
        if gdt.validate(val):
            gdt.val(val)
        return self.empty()
