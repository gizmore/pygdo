from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import html
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
        return self.param_value('method').env_copy(self)

    def get_configs(self, method: Method) -> list:
        raise Exception("OOPS, get_configs not implemented.")

    def get_config_val(self, method: Method, key: str) -> str:
        raise Exception("OOPS, get_config_val not implemented.")

    def set_config_val(self, method: Method, key: str, val: str):
        raise Exception("OOPS, set_config_val not implemented.")

    def gdo_execute(self) -> GDT:
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
            out.append(f"{gdt.get_name()}({gdt.get_val()})")
        return self.reply('msg_configs', [method.gdo_trigger(), ', '.join(out)])

    def show_config(self, method: Method, key: str) -> GDT:
        return self.reply('msg_config', [method.gdo_trigger(), key, html(self.get_config_val(method, key))])

    def set_config(self, method: Method, key: str, val: str):
        old = self.get_config_val(method, key)
        self.set_config_val(method, key, val)
        new = self.get_config_val(method, key)
        return self.reply('msg_config_set', [method.gdo_trigger(), key, html(old), html(new)])
