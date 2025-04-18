from gdo.base.Method import Method


class MethodCompletion(Method):
    """
    Abstract combobox completion ajax interface
    """

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''
