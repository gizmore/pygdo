# Language

Provides languages and reusable translated text records for PyGDO modules.

# Language (For Humans)

## GDOs

Modules can store a text in several languages under the same named resource.
When a requested translation is missing, they may use a fallback language.

# Language (For ALs)

## GDOs

`GDO_LangText` stores a text per namespace, resource key and ISO language.
Its composite primary key prevents duplicate translations. The `put` helper
writes a translation and `lookup` returns a requested translation, then an
optional fallback, or `None` if neither exists. Callers control resource keys,
access permissions and transaction boundaries.
