import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / 'gdo_sync.sh'


class SyncOwnerTest(unittest.TestCase):
    def run_sync(self, *args):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'root'
            root.mkdir()
            script = root / 'gdo_sync.sh'
            script.write_bytes(SOURCE.read_bytes())
            (root / 'gdoproviders.py').write_text('print("PROVIDERS")\n')
            for name in ('mine', 'other', 'ambiguous'):
                (root / 'gdo' / name / '.git').mkdir(parents=True)
            bindir = Path(tmp) / 'bin'
            bindir.mkdir()
            git = bindir / 'git'
            git.write_text('''#!/bin/bash
repo="$PWD"
if [[ "${1:-}" == -C ]]; then repo="$2"; shift 2; fi
if [[ "${1:-}" == remote ]]; then
  case "$repo" in
    */mine/.git/..) echo git@github.com:gizmore/one.git ;;
    */other/.git/..) echo https://github.com/mira-gpt/two.git ;;
    */ambiguous/.git/..) printf 'git@github.com:gizmore/x.git\\ngit@github.com:someone/y.git\\n' ;;
    */root) echo ssh://git@github.com/gizmore/core.git ;;
    *) exit 1 ;;
  esac
else
  echo "GIT $PWD $*"
fi
''')
            git.chmod(0o700)
            return subprocess.run(['bash', str(script), *args], input='\n', text=True,
                                  capture_output=True, cwd=root,
                                  env={**os.environ, 'PATH': f'{bindir}:{os.environ["PATH"]}'})

    def test_default_selects_gizmore_only(self):
        result = self.run_sync('test message')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Owner: gizmore', result.stdout)
        self.assertIn('/gdo/mine', result.stdout)
        self.assertNotIn('/gdo/other', result.stdout)
        self.assertNotIn('/gdo/ambiguous', result.stdout)
        self.assertIn('PROVIDERS', result.stdout)

    def test_explicit_owner_does_not_touch_other_core_or_modules(self):
        result = self.run_sync('--owner=mira-gpt', 'test message')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('/gdo/other', result.stdout)
        self.assertNotIn('/gdo/mine', result.stdout)
        self.assertNotIn('/gdo/ambiguous', result.stdout)
        self.assertNotIn('PROVIDERS', result.stdout)
        self.assertIn('Skipping core:', result.stdout)

    def test_empty_owner_fails_before_sync(self):
        result = self.run_sync('--owner=', 'test message')
        self.assertEqual(2, result.returncode)
        self.assertNotIn('GIT ', result.stdout)
