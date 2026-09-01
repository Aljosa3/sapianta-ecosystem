# G77-256GW Future Host Checkpoint Owner Binding V1

Status: future-only repository binding; no operational authority.

Generation: G77-256GW.

Canonical owner:
`.github/governance/evidence/g77_256er_p11_operational_v1/checkpoint/G77_256ER_ATOMIC_CHECKPOINT_WRITER_V1.py`.

Certified owner SHA-256:
`74047ee7b3bf219fa70491536d9a5e75eb98d92d06763a17d2783d8882a3ee1e`.

## Scope

This binding applies to future instances of exactly these two host lifecycle
checkpoint classes:

- `*_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json`;
- `*_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json`.

It does not modify, repair, normalize, or supersede any historical checkpoint.
In particular, all G77-256GV evidence remains byte-identical.

## Owner chain

The generation-specific host finalizer remains the source owner for the
observed lifecycle facts. It does not own serialization, canonicalization,
inner sealing, persistence, or persisted-byte authentication.

The existing ER atomic checkpoint writer is the checkpoint-envelope,
serialization, canonicalization, inner-seal, persistence, and independent
reread owner. Its `persist` entry point is the only bound persistence entry
point for the two future classes in scope. Its `authenticate_path` entry point
is the validation and consumer boundary.

No second lifecycle owner, checkpoint writer, validator dialect, production
route, launcher, receipt subsystem, or authorization model is created.

## Canonical byte contract

For one exact final sealable checkpoint payload `P`, the required identity is:

```text
CANONICAL_BYTES(P)
= UTF8(JSON_SORT_KEYS_COMPACT_ALLOW_NAN_FALSE(P) + LF)

checkpoint_sha256
= SHA256(CANONICAL_BYTES(P))
```

The envelope field set is exactly `checkpoint`, `checkpoint_sha256`, and
`schema_id`. The full persisted envelope is also `CANONICAL_BYTES(envelope)`.
The owner must independently reread and reauthenticate those persisted bytes.

Hashing compact JSON without the final LF is prohibited. Direct envelope
assembly followed by a separate write is not a conforming producer path.

## Binding rule

Future host pre-teardown and host teardown checkpoint callers shall:

1. finish the immutable payload before sealing;
2. pass that payload to the unchanged ER `persist` owner;
3. accept only the envelope and persisted bytes produced by that owner;
4. require the owner's independent reread result to pass; and
5. fail closed without fallback, repair-and-continue, or alternate
   serialization when any owner check fails.

This is `FORMALIZE -> REUSE -> BIND -> VERIFY`. The ER owner is reused
unchanged; its EX certification identity is not reconstructed.

## Historical limitation

The two committed GV checkpoint envelopes are canonical sorted compact JSON
plus LF, but their recorded inner hashes authenticate the exact same inner
payload bytes without the required LF. They remain immutable negative
regression evidence. This binding does not convert either historical inner
seal into a passing seal and does not change the independently supported GV
operational reduction.

## Authority and execution boundary

```text
CERTIFIED != AUTHORIZED
PROVIDER_CAPABILITY != EXECUTION_AUTHORITY
REQUEST != P11_ENTRY != PROTECTED_INVOCATION != PROTECTED_EFFECT
```

This repository binding authorizes no Human operational act, PRE, QEMU, VM,
P11 entry, protected invocation, protected effect, execution replay, retry,
or E05 credit. Human review remains required.
