# pygdo changelog

As this is based on phpgdo7 i introduce pygdo8.

Listed are changes in the gdo behaviour compared to phpgdo7.

- The naming convention "var" for db str and "value" for the converted values has been changed.
  It is now "val" and "value", because var is a builtin keyword in python.
- ~~GDT_Response~~ has been removed because it is not required anymore. Simply return any GDT
- ~~GDT_Method~~ has been removed because Method now inherits GDT
- The methods input dictionaries got removed because input is now directly stored in the GDTs.
  Methods still have an args array now which reflect the args as in sys.argv
- Many modules are now part of the core, because i always want them.
  in particular: Account, Admin, CLI, CSS, **DBMS**!, Dog, File, HTML, Javascript, Mail, Math and **Session**.
  Dog (the chatbot) is the main reason this project exists,
  so i made it part of the core.
  Everything now respects servers and channels with no big overhead
- ~~DBMS~~~ is not optional anymore. Also **only MariaDB** is supported and a dependency.
- ~~Session via ClientCookies~~ got removed as DB driven is just faster.
- Caching changed a lot. WSGI threads are re-used and skip lots of init code after first request.
  I got down to 2ms for a very slim installation in the beginning of coding.
  A login request, however, takes like 250ms with only a little DB stuff.
- Permission checks are now a mixin. You need to extend your Method
  [WithPermissionCheck](../gdo/base/WithPermissionCheck.py)
- The hook system got changed. There are still GDO hooks for CRUD actions,
  but for events there is now a new [event system](../gdo/base/Events.py) from scratch.
