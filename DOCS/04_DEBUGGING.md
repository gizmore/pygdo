# PyGDO Debugging Capabilities

Debugging. One of the funniest tasks during development, always there for a surprise.

In this chapter we will take a look at the excellent debugging and profiling tools that come with PyGDO.

## Database Debugging

Put the `protected.toml` `debug.db` to *1* for global query log,
or *2* for additional stacktraces for each query.

You can call `.debug()` on a single query to debug only a single query.

```
GDO_User.select().debug()
```

`GDODBException` shows the full query on an error, for easy and rapid development.
