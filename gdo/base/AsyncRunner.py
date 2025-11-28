import asyncio
from threading import Thread

from gdo.base.Application import Application


class AsyncRunner:

    INSTANCE: AsyncRunner = None

    def __init__(self):
        self.__class__.INSTANCE = self
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_loop, daemon=True, name="AsyncRunner")
        self.environ = Application.STORAGE.__dict__.copy()
        self._thread.start()

    def _run_loop(self):
        Application.STORAGE.__dict__.update(self.environ)
        Application.init_thread(self)
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro):
        """Run `coro` (an async function call) and return its result synchronously."""
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result()  # this blocks the caller until coro is done
