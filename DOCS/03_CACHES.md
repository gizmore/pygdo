# PyGDO Caches

PyGDO uses several caches with different lifetimes and scopes. The main
implementation is [`gdo/base/Cache.py`](../gdo/base/Cache.py).

## Process-local caches

`Cache` keeps metadata and objects in the current Python process:

- `TCACHE` stores one table object per GDO class.
- `CCACHE` stores the GDT columns and components for a GDO class.
- `PCACHE` stores the primary-key GDTs used to build object identities.
- `OCACHE` stores cached GDO instances by table name and ID. This is the
  single-identity cache: a persistent row should resolve to one in-memory GDO
  instance per process.
- `MCACHE` stores timed values until their `Application.TIME` deadline.

GDO classes opt into object caching through `gdo_cached()`. Non-persistent GDO
tables are tracked separately so their object cache can be cleared between
requests when required.

Modules and other Python `lru_cache`/`functools.cache` users also retain state
for the lifetime of the worker process. A web or ASGI request clears the
non-persistent object cache through `Cache.clear_ocache()`; it does not rebuild
the whole process.

## Optional Redis cache

Redis is configured through `redis.enabled`, `redis.host`, `redis.port`,
`redis.db`, `redis.uds`, and `redis.zlib_level`. When enabled, `Cache.RCACHE`
stores serialized values under namespaced keys of the form:

```text
<key>:<args_key>
```

`Cache.get()` and `Cache.set()` are no-ops apart from returning defaults or the
given value when Redis is disabled. The `gdo_redis_cached()` decorator hashes
arguments (including the current language) and uses this shared cache.

Redis is shared by processes, unlike `TCACHE`, `CCACHE`, `PCACHE`, `OCACHE`, and
`MCACHE`. It is also used by IPC timestamps and other explicitly Redis-backed
features; do not assume that every Redis key contains a GDO row.

## Transactions and object caches

GDO cache updates and deletions performed through `Cache.update_for()` and
`Cache.obj_search_gid(..., delete=True)` are tracked while an application-owned
transaction is active. On rollback, their process-local entries are evicted and
their Redis keys are removed; a subsequent lookup reloads from the database.
References already held by callers are not refreshed and must be discarded or
reloaded. Outermost commit clears the tracking set without evicting the entries.
If Redis eviction fails, rollback state is still reset and the cache error is
propagated; shared entries may then require separate invalidation.
An absent object ID targets the exact empty-suffix key, never the whole table
namespace.

This is rollback cleanup, not transaction isolation for the caches: updates may
be visible in process-local or Redis caches before commit. Raw SQL changes are
not automatically tracked. Permission-sensitive code should consult the
authoritative database and not rely on a cached value for access decisions.

## Cache clearing

- `Cache.clear_ocache()` clears only non-persistent object instances. This is
  the normal request-boundary operation.
- `Cache.clear()` resets process-local cache structures, removes all Redis keys
  through `Cache.remove()`, and empties the application `cache/` directory.
  Treat it as a broad maintenance operation.
- `Cache.remove(key, args_key)` removes one Redis value, all values below a key
  prefix, or the complete Redis database when called without a key. The
  no-argument form is destructive to every cache user in the configured Redis
  database.

After changing code that affects cached module metadata or assets, restart the
relevant worker or use the project’s cache-clear tooling. Inspect the target
configuration before clearing shared Redis storage.
