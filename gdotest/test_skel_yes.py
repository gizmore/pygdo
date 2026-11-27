import unittest
import json
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
            files.put_contents.assert_any_call(
                '/tmp/skel-test/__init__.py',
                'from gdo.video.module_video import module_video\n',
            )
            package = next(call.args[1] for call in files.put_contents.call_args_list
                           if call.args[0] == '/tmp/skel-test/package.json')
            self.assertEqual({}, json.loads(package)['dependencies'])

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
