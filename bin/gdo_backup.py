#!/usr/bin/env python3
"""Create a private PyGDO database and files backup from an explicit config."""
import argparse
import os
import re
import socket
import stat
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from gdo.base.Backup import Backup


def private_backup_directory(target: Path) -> bool:
    if not stat.S_IMODE(target.stat().st_mode) & 0o077:
        return True
    try:
        result = subprocess.run(['getfacl', '-cp', str(target)], check=True,
                                capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    required = {'user::', 'group::', 'other::'}
    for line in result.stdout.splitlines():
        entry = line.split('#', 1)[0].strip()
        if not entry:
            continue
        if entry.startswith('default:'):
            entry = entry[len('default:'):]
        parts = entry.split(':')
        if len(parts) != 3:
            return False
        kind, name, permissions = parts
        if not line.startswith('default:'):
            required.discard(f'{kind}:{name}:')
        if kind == 'user' and name not in ('', 'mira'):
            return False
        if kind == 'group' and (name or permissions != '---'):
            return False
        if kind == 'other' and permissions != '---':
            return False
        if kind not in ('user', 'group', 'other', 'mask'):
            return False
    return not required


def quick_backup(backup: Backup, target: Path) -> Path:
    """Publish a complete private SQL dump without overwriting earlier dumps."""
    hostname = re.sub(r'[^A-Za-z0-9._-]', '-', socket.gethostname()) or 'host'
    basename = f'{datetime.now():%Y-%m-%d-%H-%M-%S}-{hostname}'
    fd, temporary_name = tempfile.mkstemp(prefix='.dump-', suffix='.tmp', dir=target)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        backup.dump_database(temporary)
        for index in range(10000):
            suffix = '' if index == 0 else f'-{index}'
            destination = target / f'{basename}{suffix}.sql'
            try:
                os.link(temporary, destination)
                return destination
            except FileExistsError:
                continue
        raise FileExistsError('too many backups with the same timestamp')
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='protected/config.toml',
                        help='PyGDO TOML config (default: protected/config.toml)')
    parser.add_argument('--files', choices=('0', '1'), default='1',
                        help='include uploads and tracked source files (default: 1)')
    parser.add_argument('--db', choices=('0', '1'), default='1',
                        help='include the database (default: 1)')
    args = parser.parse_args()
    include_files = args.files == '1'
    include_db = args.db == '1'
    if not include_files and not include_db:
        parser.error('at least one of --files or --db must be 1')
    os.umask(0o077)
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT / config_path
    try:
        with config_path.open('rb') as config_file:
            config = tomllib.load(config_file)
        db = config['db'] if include_db else {}
        files = None
        if include_files:
            files = Path(config['dir']['files'])
            if not files.is_absolute():
                files = PROJECT / files
            if not files.is_dir():
                raise ValueError('configured files directory does not exist')
        target = PROJECT / 'protected' / 'backup'
        if target.is_symlink():
            raise ValueError('backup directory must not be a symlink')
        target.mkdir(mode=0o700, parents=True, exist_ok=True)
        if files is not None and target.resolve().is_relative_to(files.resolve()):
            raise ValueError('backup directory must be outside the files directory')
        if not private_backup_directory(target):
            raise ValueError('backup directory must not be accessible by group or others')
        backup = Backup(config_path, files if files is not None else PROJECT, db)
        if not include_files:
            output = quick_backup(backup, target)
        elif include_db:
            output = backup.archive(target, include_config=False, source_root=PROJECT)
        else:
            output = backup.archive(target, include_config=False, source_root=PROJECT, include_database=False)
        print(f'Backup created: {output}')
        return 0
    except Exception as error:
        # Never print subprocess command/environment or config contents.
        print(f'Backup failed: {type(error).__name__}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
