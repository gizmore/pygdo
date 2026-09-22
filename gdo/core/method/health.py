import os
import sys

from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import Files
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_String import GDT_String
from gdo.ui.GDT_Card import GDT_Card


class health(Method):
    """Display a read-only, owner-visible health snapshot for PyGDO."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'health'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.OWNER

    @staticmethod
    def memory() -> tuple[int, int]:
        values = {}
        try:
            with open('/proc/meminfo', encoding='ascii') as meminfo:
                for line in meminfo:
                    key, value = line.split(':', 1)
                    values[key] = int(value.strip().split()[0]) * 1024
        except (OSError, ValueError, IndexError):
            return 0, 0
        total = values.get('MemTotal', 0)
        available = values.get('MemAvailable', values.get('MemFree', 0))
        return available, max(0, total - available)

    @staticmethod
    def disk() -> tuple[int, int]:
        try:
            info = os.statvfs('/')
        except OSError:
            return 0, 0
        available = info.f_bavail * info.f_frsize
        used = (info.f_blocks - info.f_bfree) * info.f_frsize
        return available, used

    @staticmethod
    def health_field(name: str, value: str) -> GDT_String:
        return GDT_String(name).initial(value)

    def gdo_execute(self) -> GDT:
        cores = os.cpu_count() or 0
        load_1m = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
        load_percent = 100 * load_1m / cores if cores else 0.0
        memory_available, memory_used = self.memory()
        disk_available, disk_used = self.disk()

        card = GDT_Card().title('health')
        card.get_content().add_fields(
            self.health_field('gdo_revision', GDO_Module.CORE_REV),
            self.health_field('health_python', sys.version.split()[0]),
            self.health_field('health_cpus', str(cores)),
            self.health_field('health_load', f'{load_percent:.1f}% ({load_1m:.2f})'),
            self.health_field('health_mem', Files.human_file_size(memory_available)),
            self.health_field('health_used', Files.human_file_size(memory_used)),
            self.health_field('health_hdd_free', Files.human_file_size(disk_available)),
            self.health_field('health_hdd_used', Files.human_file_size(disk_used)),
        )
        return card
