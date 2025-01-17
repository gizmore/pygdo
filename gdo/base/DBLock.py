from gdo.base.Application import Application


class DBLock:
    lock_name: str
    timeout: int
    locked: bool

    def __init__(self, lock_name: str, timeout: int = 10):
        self.lock_name = lock_name
        self.timeout = timeout
        self.locked = False

    def __enter__(self):
        if Application.db().lock(self.lock_name, self.timeout):
            self.locked = True
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.locked:
            Application.db().unlock(self.lock_name)
