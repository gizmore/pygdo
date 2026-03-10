from gdo.base.GDT import GDT
from gdo.core.GDT_Dict import GDT_Dict
from gdo.core.MethodCompletion import MethodCompletion
from gdo.table.GDT_Search import GDT_Search


class file_completion(MethodCompletion):
    
    def gdo_execute(self) -> GDT:


        return GDT_Dict()