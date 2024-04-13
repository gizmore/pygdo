class WithEnv:

    _user: object

    def user(self, user):
        self._user = user
        return self

    def gdo_permission(self):
        pass
