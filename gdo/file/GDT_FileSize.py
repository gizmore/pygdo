from gdo.base.Render import Mode
from gdo.core.GDT_UInt import GDT_UInt


class GDT_FileSize(GDT_UInt):

    @staticmethod
    def to_human(bytes_size: int, decimal_places: int = 2) -> str:
        if bytes_size is None:
            pass
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        index = 0
        while bytes_size >= 1024 and index < len(units) - 1:
            bytes_size /= 1024
            index += 1
        return f"{bytes_size:.{decimal_places}f} {units[index]}"

    def render(self, mode: Mode = Mode.render_html):
        return self.to_human(self.get_value())
