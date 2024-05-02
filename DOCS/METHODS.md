## Methods

All methods inherit from the base [Method](../gdo/base/Method.py) class.
Simply overwrite gdo_parameters() and gdo_execute(),
and for [MethodForm](../gdo/form/MethodForm.py),
additionally implement gdo_form([GDT_Form](../gdo/form/GDT_Form.py))
and decorate it.


### List of abstract method classes

- [Method](../gdo/base/Method.py)
- [MethodCompletion](../gdo/core/MethodCompletion.py)
- [MethodCronjob](../gdo/core/MethodCronjob.py)
- [MethodForm](../gdo/form/MethodForm.py)


### List of methods

 - [core.echo](../gdo/core/method/echo.py) - Print the parameters back
 - [core.health](../gdo/core/method/health.py) - Print server statistics
