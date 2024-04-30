from gdo.base.Method import Method


class MethodCompletion(Method):
    """
    Abstract combobox completion ajax interface
    """

    def cli_trigger(self) -> str:
        return ''
