import mimetypes
from os import path

from gdo.base.Application import Application
from gdo.base.GDT import GDT


class GDT_FileOut(GDT):
    _path: str
    _handle: any

    def path(self, path: str):
        self._path = path
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if not hasattr(self, '_handle'):
            self._handle = open(self._path, 'rb')
        chunk = self._handle.read(int(Application.config('fileblock_size', "4096")))
        if chunk:
            return chunk
        else:
            self._handle.close()
            raise StopIteration
