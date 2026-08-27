from glob import glob

from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.MethodCompletion import MethodCompletion
from gdo.table.GDT_Search import GDT_Search


class file_completion(MethodCompletion):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Search('q').not_null().minlen(2),
            GDT_Bool('file').not_null(),
            GDT_Bool('dir').not_null(),
        ]

    def gdo_completion_items(self) -> list[dict[str, str]]:
        q = self.get_query()
        file = self.param_value('file') and False
        dir = self.param_value('dir')
        result = []
        if dir and Files.is_dir(q):
            result.append({
                'id': q,
                'var': q,
                'display_var': q,
            })
        if file and Files.is_file(q):
            result.append({
                'id': q,
                'var': q,
                'display_var': q,
            })

        for path in glob(f"{q}*", include_hidden=True):
            if file and not Files.is_file(path):
                continue
            if dir and not Files.is_dir(path):
                continue
            result.append({
                'id': path,
                'var': path,
                'display_var': path,
            })
        return result
