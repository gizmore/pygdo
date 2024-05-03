[# PyGDOv8 Coding guidelines

PyGDO coding styles and guidelines.

## Contributing

You are **not** even **allowed** to install anything from this repository,
but if i cannot stop you and you want to contribute;
[Get in touch](mailto:gizmore@wechall.net)!
Of course i am also happy about bug reports.


## Code Style

I use PyCharm for development and will release my [PyCharm Settings](../DEV/PyCharm)
so the project agrees on some aspects of Python Programming.


## Type hinting

I do not annotate everything, especially i often omit return values.
Return -> Self is always omitted, because somehow it does not work in PyCharm nicely :(

PyGDO has a lot of circular dependencies in the core and base module.
In extension modules it is better.


## Testing

PyGDO8 uses the unittest extension to test if it's operational, and is quite test driven.
You can run 3 different test suites, which all will include the `protected/config_test.toml`.
You can also run any test file separately. Rarely some test files have chaining test dependencies,
but only for the single test file, not across tests.
**But**... You have to run the core tests at least once, before you can run tests for an extension module.
If you want to develop with unittests nicely, make your `protected/config.toml` the same as the test config.


- [gdotest.py](../gdotest.py) - for all core tests in the root [gdotest](../gdotest) folder.
- [gdotestothers.py](../gdotestothers.py) - for all available extension modules.
- [gdotestall.py](../gdotestall.py)) - for running both test suites above.
  Reason is that the finish core test is run last in all suites,
  which checks for overall inconsistencies when all tests have run.

## Class inheritance

PyGDO makes use of multi inheritance a lot. The most right inheritance, the base (super)class is a GDT.
Then there are mixins which are named "WithFoo" etc. Example [WithInput](../gdo/base/WithInput.py).
Do **not** add any attribute to the GDT superclass.

Sadly i cannot use `__slots__` everywhere, because of the multi inheritance,
but at least the [GDO](../gdo/base/GDO.py) objects are slotted.


## File and Dir paths

Dirs end with a slash (/)
Files do not.
This way you can distinguish quicker, and it's nice to have this rule.

## Variable naming

- All class attributes are prefixed with "_" regardless of visibility.
  This is because else some of the names would shadow builtins.

- Static class variables are UPPERCASE without a prefix.

## Method naming

- Private methods have a "_" prefix.

- Methods prefixed with "**gdo_**" are intended to be overwritten by child classes.
Example: _gdo_columns()_ in GDO to specify db columns.

- Setters are named like the attribute without any prefix.
  Example __env_server()__ in [WithEnv](../gdo/base/WithEnv.py).
  Setters should return self.

- There are no getters, unless you would need to compute a value to get.
  Those getters are prefixed with "get_".


## Module structure

**All** Modules have to reside in the [pygdo/gdo/](../gdo) folder.
Core and extensions are mixed there,
and you can only distinguish them by the absence of the `.git` folder.
All modules are shipped with source, and to add a module you clone it under its name inside `gdo/`.

The following file and folder names are magic inside a module dir:

- module_{modulename}.py (The main module file. Has to be lowercase and only a class that extends GDO_Module)
- lang/ (should contain a file "{modulename}_en.toml" and possibly more languages.
- method/ (contains all module methods)
- README.md (Should exist)
- LICENSE (Should exist)
- test/ (For unittest)

You can use `./gdo_adm.sh skeleton modulename` to create a module skeleton for convenience.

The following file and folder names are recommended:

- css/ (for CSS assets)
- js/ (for JS assets)
- img/ (for images)

