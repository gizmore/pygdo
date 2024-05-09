from gdo.core.GDT_Object import GDT_Object


class GDT_User(GDT_Object):
    _same_server: bool
    _same_channel: bool
    _authenticated: bool

    def __init__(self, name):
        super().__init__(name)
        from gdo.core.GDO_User import GDO_User
        self.table(GDO_User.table())

    def same_server(self, same_server: bool):
        self._same_server = same_server
        return self

    def same_channel(self, same_channel: bool):
        self._same_channel = same_channel
        return self

    def authenticated(self, authenticated: bool):
        self._authenticated = authenticated
        return self

    def online(self, online: bool = True):
        return self.authenticated(online)


