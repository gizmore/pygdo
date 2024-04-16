from gdo.base.Method import Method


class welcome(Method):

    def gdo_execute(self):
        return self.message('msg_gdo_working')
