import threading

from gdo.base.Application import Application


class Thread(threading.Thread):
    ALL: list = []

    def __init__(self):
        super().__init__()
        self.daemon = True
        self._running = True

    def run(self):
        Application.init_thread(self)
        self.ALL.append(self)

    @classmethod
    def join_all(cls):
        for t in cls.ALL:
            t.join()
