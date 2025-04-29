# ToC

## Coding Conventions

### Variable names, Getters and Setters

All class member variable names start with an underscore(_) Example: _min_len
Setters are named like the getter, def min_len(len:int) -> Self, they can be chained.
There are no getters unless they compute a value, : def getMinMaxTuple()


### PyGDO Inheritance

There are basically three monster base classes.

 - [GDT](../gdo/base/GDT.py) (Gizmore Data Types)
 - [GDO](../gdo/base/GDO.py) (Gizmore Data Object - which is a GDT)
 - [Method](../gdo/base/Method.py) (Method with GDT parameters - which is a GDT)

All methods that must or can be overwritten are prefixed with 'gdo_'. Examples: gdo_parameters(), gdo_execute(), gdo_columns()


