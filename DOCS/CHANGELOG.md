# pygdo changelog

As this is based on phpgdo7 i introduce pygdo8.

Listed are changes in the gdo behaviour.

- GDT_Response has been removed because it is not required anymore. Simply return any GDT
- GDT_Method has been removed because Method now inherits GDT
- The methods input dictionaries got removed because input is now directly stored in the GDTs
Methods still have  an args array now which reflect the args as in sys.argv
- Many modules are now part of the core,
in particular: Account, Admin, Dog, File, HTML, Mail and Math.
Dog (the chatbot) is now main reason this project exists,
so i made it part of the core.
- Permission checks are now a mixin. You need to extend your Method
[WithPermissionCheck](../gdo/base/WithPermissionCheck.py)
- 