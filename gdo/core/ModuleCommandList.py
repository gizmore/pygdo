from gdo.base.Exceptions import GDODBException, GDOParamError
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.Connector import Connector
from gdo.message.GDT_Glyph import GDT_Glyph


class ModuleCommandList(Method):
    def gdo_connectors(self):
        return Connector.text_connectors()

    def gdo_execute(self):
        message = getattr(self, '_message', None)
        if message and message._env_channel:
            message.reply_privately(notice=True)
        module_name = self.gdo_trigger()
        commands = set()
        for klass in ModuleLoader.instance()._methods.values():
            method = klass()
            if method.gdo_module().get_name != module_name or method.gdo_trigger() == self.gdo_trigger():
                continue
            method.env_copy(self)
            # The default hidden policy compacts this module in general help.
            # Explicit per-method overrides still hide genuinely private methods.
            explicitly_hidden = (getattr(type(method), 'gdo_method_hidden', None) is not Method.gdo_method_hidden
                                 and method.gdo_method_hidden())
            if explicitly_hidden or not method.allows_connector():
                continue
            try:
                if method.has_permission(self._env_user, False):
                    commands.add(method.gdo_trigger())
            except (GDOParamError, GDODBException):
                continue
        return GDT_Glyph(module_name.title() + ' commands: ' + ', '.join(sorted(commands)))
