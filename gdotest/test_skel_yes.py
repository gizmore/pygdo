import unittest
from unittest.mock import patch

from gdoadm import App


class SkeletonConfirmationTest(unittest.IsolatedAsyncioTestCase):
    async def test_yes_skips_prompt(self):
        with patch('sys.argv', ['gdoadm.py', 'skel', 'video', '--yes']), \
                patch('gdoadm.Application.file_path', return_value='/tmp/skel-test/'), \
                patch('gdoadm.Files') as files, \
                patch('builtins.input', side_effect=AssertionError('unexpected prompt')):
            files.is_dir.return_value = True
            await App().skel()
            self.assertTrue(files.put_contents.called)

    async def test_without_yes_still_prompts_before_writing(self):
        with patch('sys.argv', ['gdoadm.py', 'skel', 'video']), \
                patch('gdoadm.Application.file_path', return_value='/tmp/skel-test/'), \
                patch('gdoadm.Files') as files, \
                patch('builtins.input', side_effect=EOFError) as prompt:
            files.is_dir.return_value = True
            with self.assertRaises(EOFError):
                await App().skel()
            prompt.assert_called_once()
            files.put_contents.assert_not_called()
