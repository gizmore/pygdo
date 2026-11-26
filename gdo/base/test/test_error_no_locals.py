import unittest
from uuid import uuid4
from unittest.mock import patch

from gdo.base.Logger import Logger


class TestErrorNoLocals(unittest.TestCase):
    def test_traceback_omits_locals_by_default(self):
        secret = uuid4().hex
        try:
            raise ValueError('test error')
        except ValueError as error:
            with patch('gdo.base.Logger.Console') as console:
                Logger.traceback(error)
                self.assertNotIn(secret, str(console.call_args))
            self.assertNotIn(secret, Logger.traceback(error))

