from __future__ import annotations

import os
import stat
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from gdo.mail.Mail import Mail


class Backup:
    """Back up database, configuration and uploaded files; source code lives in Git."""

    def __init__(self, config_path: str | Path, files_dir: str | Path, db_config: dict[str, str]):
        self.config_path = Path(config_path).resolve()
        self.files_dir = Path(files_dir).resolve()
        self.db_config = db_config

    def archive(self, target_dir: str | Path, timestamp: datetime | None = None, *, include_config: bool = True, source_root: Path | None = None) -> Path:
        target_dir = Path(target_dir).expanduser().resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        stamp = timestamp or datetime.now()
        target = self._new_target(target_dir, stamp)
        with tempfile.TemporaryDirectory(prefix='pygdo-backup-') as temporary:
            dump = Path(temporary) / 'database.sql'
            self.dump_database(dump)
            try:
                with ZipFile(target, 'x', ZIP_DEFLATED) as archive:
                    archive.write(dump, 'database.sql')
                    if include_config:
                        archive.write(self.config_path, 'protected/config.toml')
                    self._add_files(archive)
                    if source_root is not None:
                        self._add_tracked_source(archive, source_root)
                return target
            except Exception:
                target.unlink(missing_ok=True)
                raise

    def dump_database(self, target: Path):
        command = [
            'mysqldump',
            '--single-transaction', '--routines', '--events', '--triggers',
            '--default-character-set=utf8mb4',
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--user={self.db_config['user']}",
            self.db_config['name'],
        ]
        environment = os.environ.copy()
        environment['MYSQL_PWD'] = self.db_config['pass']
        with target.open('wb') as output:
            subprocess.run(command, stdout=output, stderr=subprocess.PIPE, env=environment, check=True)

    @staticmethod
    def mail(archive: Path, recipient: str):
        Mail.from_bot().recipient(recipient).subject('PyGDO backup').body(
            'Your requested PyGDO data backup is attached. Keep this archive private.'
        ).attachment(archive).send()

    def _new_target(self, target_dir: Path, stamp: datetime) -> Path:
        name = f'pygdo-data-{stamp:%Y%m%dT%H%M%S}'
        target = target_dir / f'{name}.zip'
        index = 1
        while target.exists():
            target = target_dir / f'{name}-{index}.zip'
            index += 1
        return target

    def _add_files(self, archive: ZipFile):
        if not self.files_dir.is_dir():
            return
        for path in self.files_dir.rglob('*'):
            if path.is_file() and not path.is_symlink():
                archive.write(path, str(Path('files') / path.relative_to(self.files_dir)))

    @staticmethod
    def _add_tracked_source(archive: ZipFile, source_root: Path):
        """Archive working-tree versions of tracked root and module files."""
        root = source_root.resolve()
        modules = root / 'gdo'
        repos = [root]
        if modules.is_dir():
            repos.extend(sorted(p for p in modules.iterdir()
                                if p.is_dir() and not p.is_symlink() and (p / '.git').exists()))
        for repo in repos:
            result = subprocess.run(
                ['git', '-c', f'safe.directory={repo}', '-C', str(repo), 'ls-files', '-z', '--cached'],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for entry in dict.fromkeys(result.stdout.split(b'\0')):
                if not entry:
                    continue
                path = repo / os.fsdecode(entry)
                name = (Path('source') / path.relative_to(root)).as_posix()
                # Do not dereference links into private or external trees.
                if path.is_symlink():
                    info = ZipInfo(name)
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    archive.writestr(info, os.readlink(path))
                elif path.is_file() and path.resolve().is_relative_to(root):
                    archive.write(path, name)
                elif path.exists() and not path.is_dir():
                    raise ValueError('unsupported tracked file')
