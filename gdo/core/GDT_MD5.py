import hashlib

from gdo.base.Application import Application
from gdo.core.GDT_Char import GDT_Char


class GDT_MD5(GDT_Char):
    """
    This GDT wraps hashlib for MD5 calculations.
    Else it is a GDT_Char with appropriate parameters
    """

    def __init__(self, name):
        super().__init__(name)
        self.ascii()
        self.maxlen(32)

    @classmethod
    def hash_for_str(cls, s: str) -> str:
        md5_hash = hashlib.md5(s.encode())
        return md5_hash.hexdigest()

    @classmethod
    def hash_for_file(cls, path: str) -> str:
        md5_hash = hashlib.md5()
        chunk_len = int(Application.config('file.block_size', '4096'))
        with open(path, "rb") as file:
            for chunk in iter(lambda: file.read(chunk_len), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
