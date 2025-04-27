from gdo.base.GDT import GDT
from gdo.base.Query import Type, Query
from gdo.base.Util import Arrays



class WithBulk:

    def bulk_insert_gdo(self, gdos: list, chunk_size=100):
        return self.bulk_insert_or_replace_gdo(Type.INSERT, gdos, chunk_size)

    def bulk_replace_gdo(self, gdos: list, chunk_size=100):
        return self.bulk_insert_or_replace_gdo(Type.REPLACE, gdos, chunk_size)

    def bulk_insert_or_replace_gdo(self, _type: Type, gdos: list, chunk_size=100):
        data = list(map(lambda gdo: gdo._vals.values(), gdos))
        return self.bulk_insert_or_replace(_type, self.table().columns().values(), data, chunk_size)

    def bulk_insert(self, columns: list[GDT], data: list[list], chunk_size=100):
        return self.bulk_insert_or_replace(Type.INSERT, columns, data, chunk_size)

    def bulk_replace(self, columns: list[GDT], data: list[list], chunk_size=100):
        return self.bulk_insert_or_replace(Type.REPLACE, columns, data, chunk_size)

    def bulk_insert_or_replace(self, _type: Type, gdts: list[GDT], data: list[list], chunk_size=100):
        chunks = Arrays.chunkify(data, chunk_size)
        for chunk in chunks:
            self._bulk_chunks(_type, gdts, chunk)
        return self

    def _bulk_chunks(self, _type, gdts: list[GDT], chunk: list):
        keyword = 'REPLACE' if _type == Type.REPLACE else 'INSERT'
        values = []
        for data in chunk:
            row_data = ",".join(list(map(lambda dat: GDT.quote(dat), data)))
            values.append(f"({row_data})")
        keys = ", ".join(list(map(lambda gdt: gdt.get_name(), gdts)))
        vals = ",".join(values)
        query = f"{keyword} INTO {self.gdo_table_name()} ({keys}) VALUES {vals}"
        Query().raw(query).exec()
