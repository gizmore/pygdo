import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class GdoDiffUntrackedTest(unittest.TestCase):
    def test_reports_text_sources_in_root_and_nested_repos_without_binary_or_secrets(self):
        script = Path(__file__).resolve().parents[1] / 'gdo_diff.sh'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / 'gdo' / 'example'
            nested.mkdir(parents=True)
            shutil.copy(script, root / 'gdo_diff.sh')
            for repo in (root, nested):
                subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (root / 'new file.py').write_text('print("root-source")\n')
            (nested / 'new.md').write_text('# nested-source\n')
            (nested / 'binary.py').write_bytes(b'\x00binary-content')
            (root / 'secret_key.py').write_text('do-not-print-this\n')
            (root / 'photo.png').write_text('not-source\n')
            os.symlink(root / 'new file.py', root / 'linked.py')
            result = subprocess.run(['bash', str(root / 'gdo_diff.sh')], cwd=root,
                                    text=True, capture_output=True, check=True)
        self.assertIn('root-source', result.stdout)
        self.assertIn('nested-source', result.stdout)
        self.assertNotIn('binary-content', result.stdout)
        self.assertNotIn('do-not-print-this', result.stdout)
        self.assertNotIn('not-source', result.stdout)
        self.assertNotIn('linked.py', result.stdout)

    def test_clean_repo_does_not_get_a_heading(self):
        script = Path(__file__).resolve().parents[1] / 'gdo_diff.sh'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            shutil.copy(script, root / 'gdo_diff.sh')
            # Track the script so the test repository has no untracked source.
            subprocess.run(['git', '-C', str(root), 'add', 'gdo_diff.sh'], check=True)
            result = subprocess.run(['bash', str(root / 'gdo_diff.sh')], cwd=root,
                                    text=True, capture_output=True, check=True)
        self.assertNotIn('=== ', result.stdout)

    def test_tracked_and_untracked_diffs_are_both_shown(self):
        script = Path(__file__).resolve().parents[1] / 'gdo_diff.sh'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            shutil.copy(script, root / 'gdo_diff.sh')
            tracked = root / 'tracked.py'
            tracked.write_text('old\n')
            subprocess.run(['git', '-C', str(root), 'add', 'tracked.py', 'gdo_diff.sh'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Test', '-c', 'user.email=test@example.test',
                            'commit', '-qm', 'fixture'], check=True)
            tracked.write_text('changed\n')
            (root / 'added.py').write_text('new\n')
            result = subprocess.run(['bash', str(root / 'gdo_diff.sh')], text=True,
                                    capture_output=True, check=True)
        self.assertIn('+changed', result.stdout)
        self.assertIn('+new', result.stdout)
