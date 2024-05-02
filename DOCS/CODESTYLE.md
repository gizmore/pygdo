# PyGDOv8 Coding guidelines

PyGDO coding styles and guidelines

## Class inheritance

PyGDO makes use of multi inheritance a lot. The most right inheritance, the base (super)class is a GDT.
Then there are mixins which are named "WithFoo" etc. Example [WithInput](../gdo/base/WithInput.py).
Do **not** add any attribute to the GDT superclass.


## File and dir paths

Dirs end with a slash (/)
Files do not.
This way you can distinguish quicker, and it's nice to have this rule.


## Module structure

The following file and folder names are magic inside a module dir:

- module_{modulename}.py (The main module file. Has to be lowercase and only a class that extends GDO_Module)
- lang/ (should contain a file "{modulename}_en.toml" and possibly more languages.
- method/ (contains all module methods)
- README.md (Should exist)
- LICENSE (Should exist)

The following file and folder names are recommended:

- css/ (for CSS assets)
- js/ (for JS assets)
- img/ (for images)

## Coding tips

