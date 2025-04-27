# PyGDO Caches

PyGDO has three levels for caching - not only - [GDOs](../gdo/base/GDO.py)



## 1) PyGDO Process Cache

Many computed data survives accepting a new request.

For example the modules loaded in the [ModuleLoader](../gdo/base/ModuleLoader.py)
are only loaded when the web worker process starts.

The class [Cache](../gdo/base/Cache.py) is worth a look.
There, GDO related caches are stored.

The process cache is the Cache.OCache / ObjectCache.


## 2) Redis Cache

When possible, GDO data is read from redis instead of mysql.
All GDO have a pk like `colA:colB:colC`,
where-as GDT_AutoInc() driven tables are a slightly special easier case: `colA`. 

The redis cache is also used to store other cache-worthy material.


## 3) MySQL Backend, but single identity

Every GDO read from MySQL is filtered through the Processes ObjectCache.

This ensures every row is only loaded once into memory,
and GDOs can be updated easily across the software we write.


## Cache Cleaning

