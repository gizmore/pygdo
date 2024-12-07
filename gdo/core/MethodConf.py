from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Method import GDT_Method
from gdo.core.GDT_String import GDT_String


class MethodConf(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Method('method').not_null().positional(),
            GDT_String('key').positional(),
            GDT_String('value').positional(),
        ]

    def get_method(self) -> Method:
        return self.param_value('method')

    def get_configs(self, method: Method) -> list:
        raise Exception("OOPS, get_configs not implemented.")

    def gdo_execute(self):
        method = self.get_method()
        if key := self.param_val('key'):
            if value := self.param_val('value'):
                return self.set_config(method, key, value)
            else:
                return self.show_config(method, key)
        else:
            return self.show_configs(method)

    def show_configs(self, method: Method) -> GDT:
        out = []
        for gdt in self.get_configs(method):
            out.append(gdt.get_name())
        return self.reply('msg_configs', [', '.join(out)])

    def show_config(self, method: Method, key: str) -> GDT:
        pass

    def set_config(self, method, key, value):
        pass
