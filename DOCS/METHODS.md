## Methods

All methods inherit from the base [Method](../gdo/base/Method.py) class.
Simply overwrite gdo_parameters() and gdo_execute(),
and for [MethodForm](../gdo/form/MethodForm.py),
additionally implement gdo_form([GDT_Form](../gdo/form/GDT_Form.py))
and decorate it.


## Application HTTP flow

GDO uses RewriteRules (i don't know nginx yet) to route **every** request through the pygdo application,
including assets and every single file (except .well-known).
Every request starts in index.py, selecting the appropriate method,
gathering input into a unified args array, that is almost identical to the `sys.argv` in CLI mode.
Then the method is executed and the result is rendered according to the render mode. 


## Application CLI flow

You can add the [/bin/] folder to your path and execute `pygdo` commands conveniently.
Methods use their plugged GDT with python argparser to construct the pygdo args array.
Method nesting is possible, and one can, for example run the following commands:

`pygdo mail.send giz "Hello There" I just want to send you a page: $(wget https://google.de/?q=proxy`

Here is the [mail.send](../gdo/mail/method/send.py) command.

You can also browse this method in http, call it via SMS or telegram, etc.
(Please note that most of this is still in progress)


### List of abstract method classes

- [Method](../gdo/base/Method.py)
- [MethodCompletion](../gdo/core/MethodCompletion.py)
- [MethodCronjob](../gdo/core/MethodCronjob.py)
- [MethodForm](../gdo/form/MethodForm.py)


### List of methods

 - [core.echo](../gdo/core/method/echo.py) - Print the parameters back
 - [core.health](../gdo/core/method/health.py) - Print server statistics
