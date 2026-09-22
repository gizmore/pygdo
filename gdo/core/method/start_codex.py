import subprocess
from pathlib import Path

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission


class start_codex(Method):
    """Run the one approved Mira/Codex recovery script for the owner."""

    CODEX_LAUNCHER = Path('/usr/local/bin/launch-mira-codex')

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'start_codex'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.OWNER

    def gdo_transactional(self) -> bool:
        return False

    @classmethod
    def launcher_is_safe(cls) -> bool:
        try:
            info = cls.CODEX_LAUNCHER.lstat()
        except OSError:
            return False
        return (
            cls.CODEX_LAUNCHER.is_file()
            and info.st_uid == 0
            and not (info.st_mode & 0o022)
        )

    def gdo_execute(self) -> GDT:
        if not self.launcher_is_safe():
            return self.err('err_core_start_codex_unavailable')
        try:
            subprocess.Popen(
                [str(self.CODEX_LAUNCHER)],
                cwd='/home/gizmore',
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                close_fds=True,
            )
        except OSError:
            return self.err('err_core_start_codex_unavailable')
        return self.reply('msg_core_start_codex_requested')
