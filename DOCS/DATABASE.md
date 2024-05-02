# PyGDOv8 Database Layer

Currently only MariaDB/MySQL is supported.
This may change by creating a patch set to support PostgreSQL and SQLite.

## Files

The DBA layer is inside the base module and consists of only a few files.

- [Cache.py](../gdo/base/Cache.py) - Stores GDO table objects, GDT columns and GDO instances by ID.
- [Database.py](../gdo/base/Database.py) - Connects and holds the database link. Has some auxiliary methods to create tables and locks etc.
- [Query.py](../gdo/base/Query.py) - Constructs database queries.
- [Result.py](../gdo/base/Result.py) - Holds a result set.
- [ArrayResult](../gdo/base/ResultArray.py) - (TODO) - Provides a Result.py API for hardcoded GDO lists.
- [GDO.py](../gdo/base/GDO.py) - Entity and Table object in one. Syncs a dictionary with the underlying DBMS.
  Every DB row has exactly one instance in memory, which i call "single identity cache".

On the other hand... currently, GDTs generate the table definition code,
which could be moved to Database.py as well, to create support for SQLite and other DBMS easier.

Every GDO class has one table instance,
which is the only one that holds the defined GDT columns for a GDO.

## Learning by Examples

#### 1) Single Identity Cache

`userA = GDO_User.table().get_by_id(1)`

`userB = GDO_User.table().select().order("user_id ASC").first().exec().fetch_object()`

`userA == userB` # Is True! - Single Identity Cache :)

#### 2) Composite Primary Key Support

Have a look at [GDO_UserSetting.py](../gdo/core/GDO_UserSetting.py).
It has a composite primary key and you can use it like this:

`email = GDO_UserSetting.table().get_by_id('2', 'email')'`

Composite keys are not supported in any gdo join methods, though.

#### 3) JOINs

You can either use `Query.join(...raw join str...)` or `Query.join_object('GDT_column_key')`

The latter only works if you have a
[GDT_Object](../gdo/core/GDT_Object.py) or
[GDT_Join](../gdo/core/GDT_Join.py) GDT in your GDOs `gdo_columns()`.

