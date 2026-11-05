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

## Running work in Dog through IPC

HTTP, Bash and the REPL can run in processes separate from Dog. A Python
object in one process is not shared with another: for example, a video worker
started by Dog cannot be controlled by calling a method on a new Bash process's
local video module instance. The REPL itself does not require Dog; only work
that depends on Dog's state does.

Use a public method and a separate internal IPC handler when the actual work
must run in Dog. The existing `shoutbox.shout` / `shoutbox.ipc_shout` pair is
a concrete example:

1. The public method checks the caller's permissions, validates input and, if
   needed, saves a record with its creator and request data.
2. It calls `IPC.send_to_dog('module.ipc_handler', [arg, ...])` and reports
   that the request was queued, not that Dog has completed the work.
3. The internal handler lives in `method/ipc_handler.py`, has
   `gdo_trigger()` return `''` so it is not a public chat command, verifies
   that it is running in Dog, and acts on Dog's worker or connector.

`mira.ask_mira` / `mira.ipc_faq` shows an important transaction detail: when
the handler needs a newly saved record, defer `IPC.send_to_dog` until the
enclosing transaction commits (`Application.defer_after_commit`). A direct
`send_to_dog` call does not perform that deferral. The current transport uses
Redis when configured, with a database-event fallback.

For video, `$starwars <text>` (also exposed as `video.starwars`) validates
and queues the request; `video.ipc_starwars` starts the effect on Dog's video
worker. Nested GDO calls such as `$(wget ...)` are resolved by
the normal method parser; quote the entire command in Bash so the shell does
not execute its own `$()` substitution:

```bash
pygdo '$starwars $(wget file:///absolute/path/demo.txt)'
```

The current Dog IPC executor invokes handlers as the internal System user; it
does not automatically preserve the original caller's identity or return a
handler result to Bash/HTTP. Therefore enforce authorization at the public
entry point, treat IPC payloads as untrusted, limit who can enqueue them, and
never use the System identity as evidence of the original caller's rights.
If execution needs the caller's identity or asynchronous results, design an
explicit verified identity and request/result record or correlation mechanism.
If Dog is down or the worker is unavailable, a queued response is not proof of
execution; expose failure/status separately where the workflow needs it.


### List of abstract method classes

- [Method](../gdo/base/Method.py)
- [MethodCompletion](../gdo/core/MethodCompletion.py)
- [MethodCronjob](../gdo/core/MethodCronjob.py)
- [MethodForm](../gdo/form/MethodForm.py)


### List of methods

 - [core.echo](../gdo/core/method/echo.py) - Print the parameters back
 - [core.health](../gdo/core/method/health.py) - Print server statistics
