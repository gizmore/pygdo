import asyncio
import os
from pathlib import Path

from gdo.base.Application import Application
from gdo.base.Backup import Backup
from gdo.base.Method import Method
from gdo.core.Connector import Connector
from gdo.core.GDO_Permission import GDO_Permission


class backup_make_now(Method):

    def gdo_method_hidden(self) -> bool:
        return True
    @classmethod
    def gdo_trigger(cls) -> str:
        return 'backup.make_now'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.OWNER

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    async def gdo_execute(self):
        target = Path(Application.file_path('protected/backup/full-private'))
        files = Path(Application.file_path(Application.config('dir.files'))).resolve()
        if target.is_symlink():
            raise ValueError('Backup directory must not be a symlink')
        target.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = target.stat()
        if info.st_uid != os.geteuid() or info.st_mode & 0o077:
            raise ValueError('Backup directory must be private and owned by the current user')
        if not files.is_dir() or target.resolve().is_relative_to(files):
            raise ValueError('Files directory must exist and exclude the backup directory')
        backup = Backup(Application.CONFIG_PATH, files, {
            'host': Application.config('db.host'),
            'port': Application.config('db.port'),
            'name': Application.config('db.name'),
            'user': Application.config('db.user'),
            'pass': Application.config('db.pass'),
        })
        archive = await asyncio.to_thread(backup.archive, target)
        archive.chmod(0o600)
        return self.reply('msg_backup_now_created', (str(archive),))
