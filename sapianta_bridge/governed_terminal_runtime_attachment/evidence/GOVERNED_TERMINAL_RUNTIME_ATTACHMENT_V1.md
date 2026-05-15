# GOVERNED_TERMINAL_RUNTIME_ATTACHMENT_V1

This milestone creates the first bounded governed terminal runtime attachment layer.

It binds an already active governed runtime serving session to explicit terminal continuity identifiers:

- `stdin_binding_id`
- `stdout_binding_id`

The layer records replay-visible attachment identity and preserves the full governed runtime lineage through response emission.

## Preserved Boundaries

- terminal attachment is not orchestration
- terminal attachment is not autonomous continuation
- terminal attachment is not unrestricted live shell access
- bounded `stdin` and `stdout` continuity do not grant provider authority
- missing terminal or runtime continuity fails closed

## Operational Meaning

This layer advances the no-copy/paste stack from governed runtime serving toward direct governed terminal interaction by making the terminal surface an explicit replay-visible attachment point. It does not execute arbitrary commands, expose unrestricted shell access, or trust hidden provider memory.
