from glob import glob

from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_List import GDT_List
from gdo.core.MethodCompletion import MethodCompletion
from gdo.table.GDT_Search import GDT_Search


class file_completion(MethodCompletion):

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Search('q').not_null().minlen(2),
            GDT_Bool('file').not_null(),
            GDT_Bool('dir').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        q = self.get_query()
        file = self.param_value('file') and False
        dir = self.param_value('dir')
        result = []
        for path in glob(f"{q}*", include_hidden=True):
            if file and not Files.is_file(path):
                continue
            if dir and not Files.is_dir(path):
                continue
            result.append({
                'id': path,
                'val': path,
                'value': path,
            })
        return GDT_List(*result)
