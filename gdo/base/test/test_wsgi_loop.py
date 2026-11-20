import asyncio
import unittest
from unittest.mock import patch

import index_wsgi
from gdo.base.Application import Application


class WSGILoopTest(unittest.TestCase):
    def test_interleaved_requests_keep_independent_loops(self):
        async def answer():
            return b'ok'

        def response(environ, start_response):
            yield b'start'
            yield index_wsgi.aiorun(answer())

        with patch.object(index_wsgi, 'pygdo_application', response):
            first = index_wsgi.application({}, None)
            second = index_wsgi.application({}, None)
            try:
                self.assertEqual(b'start', next(first))
                self.assertEqual(b'start', next(second))
                self.assertEqual(b'ok', next(second))
                self.assertEqual([], list(second))
                self.assertEqual(b'ok', next(first))
                self.assertEqual([], list(first))
            finally:
                first.close()
                second.close()

    def test_early_close_cleans_up_without_leaking_context(self):
        loops = []

        def response(environ, start_response):
            loops.append(Application.REQUEST_LOOP.get())
            yield b'start'

        with patch.object(index_wsgi, 'pygdo_application', response):
            result = index_wsgi.application({}, None)
            self.assertEqual(b'start', next(result))
            self.assertIsNone(Application.REQUEST_LOOP.get())
            self.assertFalse(loops[0].is_closed())
            result.close()
            self.assertTrue(loops[0].is_closed())
            self.assertIsNone(Application.REQUEST_LOOP.get())

    def test_run_coro_uses_request_loop(self):
        observed = []

        async def check():
            observed.append(asyncio.get_running_loop())

        def response(environ, start_response):
            expected = Application.REQUEST_LOOP.get()
            Application.run_coro(check(), 'check')
            self.assertEqual([expected], observed)
            yield b'ok'

        with patch.object(index_wsgi, 'pygdo_application', response):
            self.assertEqual([b'ok'], list(index_wsgi.application({}, None)))

    def test_exception_closes_loop_and_restores_context(self):
        loops = []

        def response(environ, start_response):
            loops.append(Application.REQUEST_LOOP.get())
            yield b'start'
            raise ValueError('test failure')

        with patch.object(index_wsgi, 'pygdo_application', response):
            result = index_wsgi.application({}, None)
            self.assertEqual(b'start', next(result))
            with self.assertRaisesRegex(ValueError, 'test failure'):
                next(result)
        self.assertTrue(loops[0].is_closed())
        self.assertIsNone(Application.REQUEST_LOOP.get())
