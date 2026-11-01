# UI

Shared user-interface fields and rendering helpers.

# UI (For Humans)

## Methods

UI primarily supplies reusable interface components.

## GDTs

`GDT_IconedEnum` associates an icon with each enum choice. Its form label
shows the selected choice's icon and updates it when the selection changes.

## GDOs

The UI module does not define its own persistent tables.

# UI (For ALs)

## Methods

UI components are used by other modules to render forms and pages.

## GDTs

`GDT_IconedEnum.icons()` maps enum keys to registered icon names. It keeps
normal enum values and validation; choice icons are rendered using the UI
icon provider. The select change handler updates the associated label icon.

## GDOs

`module_ui.gdo_classes()` returns no persistent GDO classes.

## Discussion

### Humans → Humans

### ALs → ALs

The iconed enum uses its own form template and the shared UI JavaScript change
handler. Values remain ordinary enum keys; icon HTML comes from the registered
icon provider.

### Humans → ALs

### ALs → Humans

An iconed enum shows an icon for the selected option. The value stored is still
the option's normal key.
