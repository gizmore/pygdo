
## [GDT](../gdo/base/GDT.py)

GDT means "gizmore data type".
You plug GDT into database objects (GDOs),
other GDT like GDT_Form, GDT_Table, GDT_Bar or GDT_Menu
and [Methods](./METHODS.md).

The GDT system is nicely object orientated, so we don't have to, for example,
write validators again and again.

Inside the DB you can plug GDT like GDT_Email,
borrow this field and plug it in a form or inside a table.

GDT always know how to behave, render, validate and query in all supported
[application modes](../gdo/base/Render.py).

#### Core GDTs

Here is a small collection of often used and inherited GDT.

- [GDT_String](../gdo/core/GDT_String.py)
- [GDT_Int](../gdo/core/GDT_Int.py)
- [GDT_IP](../gdo/net/GDT_IP.py)
- [GDT_Url](../gdo/net/GDT_Url.py)
- [GDT_Path](../gdo/core/GDT_Path.py)
- ...

## [GDO](../gdo/base/GDO.py) 

This is an object entity, probably using the database.
Overwrite gdo_columns() to return a list of GDTs.

 - If you (ab)use this class as a DTO, override gdo_can_persist()
 - If you inherit from your own GDO classes with polymorphism, override gdo_real_class()


