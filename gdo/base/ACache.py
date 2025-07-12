import zlib

import msgspec.msgpack
from redis.asyncio import Redis

from gdo.base import GDO
from gdo.base.WithSerialization import WithSerialization


class ACache:
    """
    Async Redis cache
    """
    #PYPP#START#
    HITS = 0
    MISS = 0
    UPDATES = 0
    REMOVES = 0
    #PYPP#END#

    ACACHE: Redis = None  # key => dict[key, WithSerialization] mapping

    @classmethod
    def init(cls, enabled: bool = False, host: str = 'localhost', port: int = 6379, db: int = 0, uds: str=''):
        pass
        # if False:
        #     if uds:
        #         cls.ACACHE = Redis(unix_socket_path=uds, decode_responses=False)
        #     else:
        #         cls.ACACHE = Redis(host=host, port=port, db=db, decode_responses=False)

    @classmethod
    async def clear(cls):
        if cls.ACACHE:
            await cls.remove()

    @classmethod
    async def obj_search_redis(cls, gdo: GDO, vals: dict, delete: bool = False):
        from gdo.base.Cache import Cache
        if gdo.gdo_cached():
            cn = gdo.gdo_table_name()
            cursor = 0
            while True:
                cursor, keys = await cls.ACACHE.scan(cursor, match=f"{cn}:*")
                for key in keys:
                    key = key.decode()
                    if rc := await cls.get(key):
                        found = True
                        for k, v in vals.items():
                            if rc.gdo_val(k) != v:
                                found = False
                                break
                        if found:
                            cls.HITS += 1 #PYPP#DELETE#
                            if delete:
                                await cls.remove(key)
                                gid = rc.get_id()
                                if id in Cache.OCACHE[cn]:
                                    del Cache.OCACHE[cn][gid]
                                    return None
                            return Cache.obj_for(rc, after_write=True, is_rc=True)
                if cursor == 0:
                    break
            cls.MISS += 1 #PYPP#DELETE#

    ##########
    # ACACHE #
    ##########

    @classmethod
    async def get(cls, key: str, args_key: str = None, default: any = None):
        if cls.ACACHE:
            key = f"{key}:{args_key}" if args_key else key
            if packed := await cls.ACACHE.get(key):
                cls.HITS += 1 #PYPP#DELETE#
                return WithSerialization.gdounpack(zlib.decompress(packed))
            cls.MISS += 1 #PYPP#DELETE#
        return default

    @classmethod
    async def set(cls, key: str, args_key: str | None, value: WithSerialization):
        if cls.ACACHE:
            if isinstance(value, WithSerialization):
                value = value.gdopack()
            else:
                value = msgspec.msgpack.encode(value)
            cls.UPDATES += 1 #PYPP#DELETE#
            key = f"{key}:{args_key}" if args_key else key
            await cls.ACACHE.set(key, zlib.compress(value))

    @classmethod
    async def remove(cls, key: str = None, args_key: str = None):
        if cls.ACACHE:
            if key is None:
                cls.REMOVES += 1 #PYPP#DELETE#
                await cls.ACACHE.flushdb()
            elif args_key is None:
                cursor = 0
                while True:
                    cursor, keys = await cls.ACACHE.scan(cursor, match=f"{key}:*")
                    if keys:
                        cls.REMOVES += 1 #PYPP#DELETE#
                        await cls.ACACHE.delete(*keys)
                    if cursor == 0:
                        break
            else:
                cls.REMOVES += 1 #PYPP#DELETE#
                redis_key = f"{key}:{args_key}"
                await cls.ACACHE.delete(redis_key)
