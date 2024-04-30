## Methods

All methods inherit from the base [Method](../gdo/base/Method.py) class.
Simply overwrite gdo_parameters(),
and for [MethodForm](../gdo/form/MethodForm.py),
additionally implement gdo_form([GDT_Form](../gdo/form/GDT_Form.py))
and decorate the form.

### List of methods

 - [core.echo](../gdo/core/method/echo.py) - Print the parameters back
 - [core.health](../gdo/core/method/health.py) - Print server statistics
