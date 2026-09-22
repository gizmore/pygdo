import re
import subprocess

from gdo.base.GDO import GDO
from gdo.base.GDOSorter import GDOSorter
from gdo.base.Result import ResultType
from gdo.base.ResultArray import ResultArray
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Process import GDO_Process
from gdo.table.MethodQueryTable import MethodQueryTable


class proc(MethodQueryTable):
    """Display local processes without exposing command arguments or a shell."""

    DEFAULT_LOAD_FILTER = '25-'

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'proc'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.OWNER

    def gdo_table(self) -> GDO:
        return GDO_Process.table()

    def gdo_order_default(self):
        return 'proc_load'

    def parameters(self, reset: bool = False):
        parameters = super().parameters(reset)
        filter_field = parameters[self.gdo_filter_name()]
        if not filter_field.get_val():
            filter_field.val({'proc_load': [self.DEFAULT_LOAD_FILTER]})
        return parameters

    @staticmethod
    def read_processes() -> list[GDO_Process]:
        """Use a fixed ps invocation and expose only its executable name."""
        try:
            result = subprocess.run(
                ['ps', '-eo', 'pid=,pcpu=,pmem=,comm='],
                check=False,
                capture_output=True,
                text=True,
                timeout=1,
                env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'},
            )
        except (OSError, subprocess.TimeoutExpired):
            return []

        processes = []
        for line in result.stdout.splitlines():
            parts = line.split(maxsplit=3)
            if len(parts) != 4:
                continue
            try:
                pid, load, memory = int(parts[0]), float(parts[1]), float(parts[2])
            except ValueError:
                continue
            processes.append(GDO_Process.blank({
                'proc_pid': str(pid),
                'proc_load': str(load),
                'proc_memory': str(memory),
                'proc_command': parts[3],
            }))
        return processes

    @staticmethod
    def matches_load(value: float, expression: str) -> bool:
        """Accept the familiar table range syntax: 25-, -25, 10-25 or 25."""
        match = re.fullmatch(
            r'\s*(?:(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)?|\-\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?))\s*',
            expression or '',
        )
        if not match:
            return True
        lower, upper, at_most, exact = match.groups()
        if exact is not None:
            return value == float(exact)
        if at_most is not None:
            return value <= float(at_most)
        if upper is None:
            return value >= float(lower)
        return float(lower) <= value <= float(upper)

    def filter_processes(self, processes: list[GDO_Process]) -> list[GDO_Process]:
        filters = self.table_filter_field().get_val() or {}
        load_values = filters.get('proc_load', [])
        if isinstance(load_values, str):
            load_values = [load_values]
        for expression in load_values:
            if expression:
                processes = [
                    process for process in processes
                    if self.matches_load(float(process.gdo_val('proc_load')), expression)
                ]
        for name, values in filters.items():
            if name == 'proc_load':
                continue
            if isinstance(values, str):
                values = [values]
            if values:
                processes = [
                    process for process in processes
                    if any(str(value).casefold() in str(process.gdo_val(name) or '').casefold() for value in values if value)
                ]
        return processes

    def processed_rows(self, paginated: bool) -> list[GDO_Process]:
        rows = self.apply_table_search_result(self.read_processes())
        rows = self.filter_processes(rows)
        if self.gdo_ordered():
            rows = GDOSorter.sort(rows, self.table_order_field())
        if paginated and self.gdo_paginated():
            rows = GDOSorter.paginate(rows, self.table_paginate_field(), self.gdo_paginate_size())
        return rows

    def get_num_results(self) -> int:
        return len(self.processed_rows(False))

    def get_table_result(self) -> ResultArray:
        return ResultArray(self.processed_rows(True), self.gdo_table()).iter(ResultType.OBJECT)

    @staticmethod
    def render_proc_load(field, _process) -> str:
        return f'{field.render()}%'

    @staticmethod
    def render_proc_memory(field, _process) -> str:
        return f'{field.render()}%'
