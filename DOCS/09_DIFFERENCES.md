# PyGDO Differences

This page describes differences from other frameworks you may be used to.


## Execution chain

- Middleware is not configurable. Modules, by priority, hook into gdo_init().
  Nobody wants to configure middleware.

- There are no special webserver rules for assets.
  Every request is piped through index.py, protecting your files to the max.

- There is no webpack or similar. All assets are used in their dev version from source.
  However, there is a [minify](https://github.com/gizmore/pygdo-minifier) module
  that bundles **all** assets into a single file with the press of F5.
  Without that module, debugging is a real joy. Sadly no typescript.


## Type System

- There are not 2 or 3 or maybe more typesystems, like DB, JS, Django, third party,
  but only **one** unified type system: GDT.
  Fancy types are available, like [GDT_Email](../gdo/mail/GDT_Email.py), which
  automatically create validators, DB columns and care of the rendering in various modes.


## DBA

- The DBA layer does not feature annotations for relations.
  Instead, you plug GDT_Object and GDT_Join in your GDO.columns() definition
  and can use them easily with Query.join_object().

- There are no handwritten migration files.
  Instead, there is auto migration which automatically migrates GDOs to the current version.
  Never ever write a migration file!

- Ever wondered why composite primary keys are not supported but it would be such a blast?
  Well, in the GDO DBA, this is supported.
  But you cannot have a GDT_Object for a table with composite primary keys (yet).


## JS and CSS assets Toolchain

- There is an F5 toolchain which loads all JS and CSS from source,
  which means you can debug and play with Code nicely.

- No Typescript support

- There are modules that turn the F5 into a caching of compressed and obfuscated asset files.
  Still F5 toolchain, but **all** assets are compiled into a single JS/CSS file.
  It is not possible to request any .js and .css file from the gdo folder then.
