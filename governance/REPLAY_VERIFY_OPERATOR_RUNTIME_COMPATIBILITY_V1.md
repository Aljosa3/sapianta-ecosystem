# REPLAY_VERIFY_OPERATOR_RUNTIME_COMPATIBILITY_V1

## Status

`REPLAY_VERIFY_OPERATOR_RUNTIME_COMPATIBILITY_STATUS = READY`

## Purpose

This milestone makes the existing `aigol replay verify` command compatible with the existing operator runtime replay format.

It does not introduce a new replay architecture, replay model, governance layer, authority concept, worker behavior, provider behavior, authorization behavior, or operator interface.

## Problem

Operator runtime replay already exists under:

```text
.aigol_operator_runtime/<operation_id>/
  provider/
  authorization/
  worker/
```

`aigol replay operation` can reconstruct it.

Before this compatibility fix, `aigol replay verify` delegated only to governed-return ledger continuity and could report:

```text
status = VERIFY_FAILED
ledger_entry_exists = False
```

even when operator replay evidence existed.

## Compatibility Behavior

`aigol replay verify` now checks whether the supplied replay identity is an operator runtime operation directory.

If operator replay exists, verification reconstructs:

- provider replay;
- authorization replay;
- worker replay;
- replay hashes;
- operation lineage;
- execution status.

If operator replay does not exist, verification falls back to the existing governed-return verification path.

## Verified Operator Evidence

Operator replay verification checks:

- replay directory exists;
- provider evidence exists;
- authorization evidence exists;
- worker evidence exists;
- provider replay hash is present;
- authorization replay hash is present;
- worker replay hash is present;
- replay lineage is reconstructable;
- operation replay summary has six expected events.

## Fail-Closed Behavior

The compatibility path returns `VERIFY_FAILED` for:

- missing replay;
- missing evidence;
- corrupt evidence;
- broken replay structure;
- broken lineage.

## Boundary

This milestone does not add:

- replay migration;
- replay V2;
- new authority;
- new governance;
- worker changes;
- provider changes;
- authorization changes;
- operator command changes.

## Final Classification

```text
REPLAY_VERIFY_OPERATOR_RUNTIME_COMPATIBILITY_STATUS = READY
```
