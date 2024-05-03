# PyGDO Templates

## [GDT_Template](../gdo/core/GDT_Template.py)

I am using a custom patched "[Templite](../gdo/core/GDT_Template.py)", which is a minimal template engine.
The original source is hard to find.
It only features python code with <%%> or <%=%> and treats the rest as strings to output.

As a template is just python code you have to supply all symbols you need in a template in the args parameter.
I usually add `"field": self` there.

Examples:

- [form_string.html](../gdo/core/tpl/form_string.html) example
- [page.html](../gdo/ui/tpl/page.html) example


### Rendering a template

You render a template with `GDT_Template.python(module_name, file_name, args)`.

Example from [GDT_String](../gdo/core/GDT_String.py):

```
return GDT_Template.python('core', 'form_string.html', {'field': self})
```

You can also use GDT_Template as a normal GDT like this:

```
gdt = GDT_Template().template('core', 'page.html', args)
```

Then you can plug the GDT anywhere you like or need.

### Predefined args

The template engine fills the args with some predefined variables:

- modules - The loaded modules from the [ModuleLoader](../gdo/base/ModuleLoader.py) _cache.
- Mode - The application rendering [Mode](../gdo/base/Render.py) class.
- Application - The [Application](../gdo/base/Application.py) class.
- t - The basic translation method from [Trans](../gdo/base/Trans.py).
- time - The [Time](../gdo/date/Time.py) helper class.

Templite provides the following variables by default:

- include - A method to include another template file.
- write - A method to output a string to the template renderer.
- writeln - Same as write, just an additional newline. 