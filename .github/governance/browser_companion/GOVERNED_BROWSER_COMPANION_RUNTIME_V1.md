# GOVERNED_BROWSER_COMPANION_RUNTIME_V1

This milestone creates the first minimal browser companion for explicit,
human-triggered invocation of the already-governed localhost runtime.

## Scope

- local-only endpoint: `http://127.0.0.1:8110/governed-invoke`
- explicit popup input plus click action
- deterministic governed preview request construction
- concise replay-visible response display

## Boundaries

- no agents, orchestration, retry, fallback, or hidden continuation
- no broad page scraping or credential capture
- no automatic prompt submission
- no public runtime exposure
- no broad browser host permissions

The companion is a user-controlled interaction bridge. It does not interpret
arbitrary ChatGPT content as executable authority.
