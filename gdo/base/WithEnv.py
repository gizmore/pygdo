

class WithEnv:
    _user: object
    _session: object

    def user(self, user):
        self._user = user
        return self

    def session(self, session):
        self._session = session
        return self

    def cli_session(self):
        from gdo.core.GDO_Session import GDO_Session
        self._session = GDO_Session.for_user(self._user)
        return self

    def gdo_permission(self):
        pass
