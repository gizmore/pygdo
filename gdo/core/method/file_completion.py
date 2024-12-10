from gdo.core.MethodCompletion import MethodCompletion


class file_completion(MethodCompletion):
    
    def gdo_connectors(self) -> str:
        return 'web'
