# Write a PyGDO Module

## Start safely

1. Create a repository and clone it into `pygdo/gdo/<module_name>`.
2. Inspect `git status`; commit any work worth preserving.
3. Generate the standard layout:

   ```bash
   ./gdo_adm.sh skel <module_name>
   ```

   `skel` deliberately overwrites core files after an interactive prompt. Run
   it before custom code, or commit first and merge the generated structure.
   When `gdo_adm.sh` still uses system Python, activate `.venv` first.

## Module layout

- `module_<module_name>.py`: subclass `GDO_Module`; module configuration,
  install hook, events, and optional web assets live here.
- `method/<name>.py`: a method class named `<name>` in the matching filename.
  PyGDO discovers methods from this filename/class pairing.
- `lang/<module_name>_en.toml`: module and method messages.
- `test/`: unit tests and module-install/render tests.
- `requirements.txt`: only direct Python dependencies.
- `js/`, `css/`, `tpl/`: optional web resources.

## Implement narrowly

1. Put reusable domain logic in a small service class, separate from chat or
   HTTP rendering.
2. Use `async def gdo_execute()` for network or database work.
3. Let GDT parameters validate method input. Keep transport-specific parsing
   out of the service.
4. Add a pure unit test for parsing/logic before an integration test.
5. Add a command method only after its argument shape and output are clear.

## Verify and publish

```bash
# Run a targeted test from pygdo/
.venv/bin/python -m unittest gdo.<module_name>.test.test_<module_name>

# Inspect before sharing
git -C gdo/<module_name> status --short
git -C gdo/<module_name> diff --check
```

Commit a coherent change first. Push only after reviewing the commit and
deciding it should be published.
