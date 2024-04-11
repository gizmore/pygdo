from gdo.core.Trans import t


class GDOException(Exception):

    def __init__(self, message):
        super().__init__(message)


class GDODBException(Exception):

    def __init__(self, error, query):
        super().__init__(f'DB-Error: {error}\nQuery: {query}')


class GDOError(Exception):
    
    def __init__(self, key, args):
        super().__init__(t(key, args))
