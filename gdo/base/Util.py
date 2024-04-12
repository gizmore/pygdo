import os.path


class Strings:
    @classmethod
    def substr_from(cls, s: str, frm: str, default='') -> str:
        """Return substring from the first occurrence of `frm` in `s`, or `default` if `frm` is not found."""
        index = s.find(frm)
        if index != -1:
            return s[index + len(frm):]
        return default

    @classmethod
    def substr_to(cls, s: str, to: str, default='') -> str:
        """Return substring up to (excluding) the first occurrence of `to` in `s`, or `default` if `to` is not found."""
        index = s.find(to)
        if index != -1:
            return s[:index]
        return default

    @classmethod
    def rsubstr_from(cls, s: str, frm: str, default='') -> str:
        """Return substring from the last occurrence of `frm` in `s`, or `default` if `frm` is not found."""
        index = s.rfind(frm)
        if index != -1:
            return s[index + len(frm):]
        return default

    @classmethod
    def rsubstr_to(cls, s: str, to: str, default='') -> str:
        """Return substring up to (excluding) the last occurrence of `to` in `s`, or `default` if `to` is not found."""
        index = s.rfind(to)
        if index != -1:
            return s[:index]
        return default

    @classmethod
    def nullstr(cls, s: str):
        """Return None on empty strings"""
        if s != '':
            return s
        return None

    @classmethod
    def html(cls, s: str):
        return s


class Files:

    @classmethod
    def exists(cls, path: str) -> bool:
        return os.path.exists(path)


class Arrays:

    @classmethod
    def unique(cls, lst):
        """Return only unique items of a list"""
        return list(set(lst))

    @classmethod
    def chunkify(cls, lst: list, chunk_size: int):
        """
        Split a list into chunks of a specified size.

        Args:
            lst (list): The list to split.
            chunk_size (int): The size of each chunk.

        Returns:
            list: A list of lists, each containing elements of the original list in chunks.
        """
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
