<<<<<<<<<<<<<<<<<<# PyGDO Ideas

A new list of ideas, mostly regarding PyGDOv8.

There is an old [list of ideas in phpgdo7](http://github.com/gizmore/phpgdo/blob/main/DOCS/GDO7_IDEAS.md)


## Ideas

Ideas are invitations to explore, not commitments. Promote an idea to
[`TODO.md`](./TODO.md) only when its next action and owner are clear.

- Guest analytics: less tracking can also mean less work on the request path.
  Consider whether a guest-online count or page counter is useful before adding
  per-request writes. A page count measures requests, not unique people, and
  may include refreshes and bots. Counts based on IP addresses merge visitors
  behind a shared network and can double-count changing addresses.
  `GDO_Session` initially sends the same placeholder cookie to everyone; a
  unique persisted session can be created when it is returned, so the
  placeholder alone cannot count guests. `sess_time` is an edited timestamp,
  not a verified per-request last-seen time; `edit_on_created(True)` can also
  initialize it on creation. Session cleanup already uses this field.
  One possible design is to count validated anonymous sessions in a short
  active window, with throttled activity updates and a cached aggregate; an
  ephemeral Redis implementation is another option. Define the window and
  failure behavior, avoid storing session credentials or unnecessary IPs, and
  benchmark the request-path and storage costs before choosing. These are
  design ideas, not measured performance results; the current page-counter
  implementation has not been verified here.
- Public interfaith text explorer: publish HTML editions of religious texts with
  stable passage anchors and sourced cross-links between traditions. Explain
  both parallels and differences without implying that passages are equivalent.
  Select the initial texts and languages, and verify publication rights for
  each source edition and translation before including it.
- Add `$core.genhelp` to generate a `HELP.md` overview from all methods' help
  content. Scope, language, permissions, and output location remain to be
  decided.
- Exception email notifications are opt-in via `mail.errors_to` (empty by default).
  Centrally logged exceptions, unhandled CLI/asyncio exceptions and web server
  failures trigger a
  best-effort SMTP notification when `mail.debug = 0`. The notification includes
  exception type, time, host, PID and stack locations, but deliberately omits
  exception messages, source lines and local variables, which can contain
  credentials or private data. Handled exceptions that are never logged are not
  intercepted. A given exception object is notified at most once per process;
  delivery failures do not produce further error emails or automatic retries.
- Translation provider interface: start with the keyless Google endpoint, then
  make other providers or local models swappable without changing methods.
- Preserve original text, source language, target language, and provider in
  translation results so humans can review or improve them later.
- Use the same GDT-backed translation method in CLI, web, IRC, TCP, and other
  connectors; the transport should not decide translation semantics.

- Weighted vote logic (5 - votecnt) –
elegant social dampening.

- annotate permission checks with @sd_perm(player=True,leader=True,itemklass=Deck,action=fight,)
- twosearch
- forum with chatgpt/other AI accounts.
- on at least one output to stderr per line => append an empty line as div to the end of the failed command.

- a mogwai mini pc that comes with gdo and a setup like ours

- a place your flag service where you can mark a cracked territory with your flag :D

- A translator helper to translate between dumb/disabled to easy english

