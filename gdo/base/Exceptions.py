from gdo.base.Trans import t


class GDOError(Exception):

    def __init__(self, key, args=None):
        from gdo.base.Trans import t
        super().__init__(t(key, args))


class GDOException(Exception):

    def __init__(self, message):
        super().__init__(message)


class GDODBException(Exception):

    def __init__(self, error, query):
        super().__init__(f"DB-Error: {error}\nQuery:\n{query}")


class GDOModuleException(Exception):
    _module: str

    def __init__(self, module_name: str):
        super().__init__(f"Unknown module: {module_name}")
        self._module = module_name


class GDOMethodException(Exception):

    def __init__(self, module_name: str, method_name: str):
        super().__init__(f"Unknown method: {module_name} / {method_name}")


class GDOValidationException(Exception):

    def __init__(self, module_name: str, key: str, val: str):
        super().__init__(t('err_gdt_validation', [module_name, key, val]))