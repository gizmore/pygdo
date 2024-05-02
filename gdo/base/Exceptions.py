from gdo.base.Trans import t

"""
All GDO Errors and Exceptions
"""


class GDOError(Exception):

    def __init__(self, key: str, args: list[str] = None):
        from gdo.base.Trans import t
        super().__init__(t(key, args))


class GDOParamError(GDOError):

    def __init__(self, key: str, args: list[str] = None):
        super().__init__(key, args)


class GDOException(Exception):

    def __init__(self, message):
        super().__init__(message)


class GDODBException(Exception):

    def __init__(self, error, query):
        super().__init__(f"DB-Error: {error}\nQuery:\n{query}\n")


class GDOModuleException(Exception):
    _module: str

    def __init__(self, module_name: str):
        super().__init__(f"Unknown module: {module_name}\n")
        self._module = module_name


class GDOMethodException(Exception):

    def __init__(self, module_name: str, method_name: str):
        super().__init__(f"Unknown method: {module_name} / {method_name}\n")


class GDOValidationException(Exception):

    def __init__(self, module_name: str, key: str, val: str):
        super().__init__(t('err_gdt_validation', [module_name, key, val]))


class GDOParamNameException(GDOException):

    def __init__(self, cmd: str, line: str):
        super().__init__(t('err_web_param_wrong', [cmd, line]))
