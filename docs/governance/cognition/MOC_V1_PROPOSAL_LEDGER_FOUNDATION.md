# MOC_V1_PROPOSAL_LEDGER_FOUNDATION

Status: append-only proposal lifecycle ledger foundation.

## Purpose

`MOC_V1_PROPOSAL_LEDGER_FOUNDATION` creates the first canonical append-only ledger for MOC V1 advisory proposal lifecycle records.

This milestone creates immutable proposal operational memory only.

Proposal does not equal execution.

## Ledger Model

The ledger stores one canonical JSON object per line in JSONL format.

Suggested default path:

```text
.runtime/aigol/moc/proposal_ledger.jsonl
```

Each ledger entry links to one valid `MOC_V1_PROPOSAL_PERSISTENCE_RECORD`.

## Ledger Entry

Each entry records:

- ledger entry identity
- proposal identity and hash
- proposal lifecycle state
- linked persistence hash
- linked contract identity and hash
- correction attempt
- lineage references
- validation references
- correction references
- approval references
- previous ledger hash
- append-only guarantee
- replay-safe guarantee
- advisory-only guarantee
- deterministic ledger entry hash

## Append-Only Guarantees

The ledger is append-only.

Prior entries are not rewritten, repaired, reordered, or compacted.

The `previous_ledger_hash` links each appended entry to the previous ledger entry when present.

## Fail-Closed Conditions

The ledger append fails closed if:

- persistence record is missing
- persistence record has invalid artifact type
- persistence hash is missing
- persistence transition is invalid
- persistence state is `FAIL_CLOSED`
- lineage references are missing
- existing ledger lines are malformed

Failed appends emit a replay-visible ledger entry artifact with `ledger_append_status: FAIL_CLOSED` and `append_performed: false`.

## Governance Boundaries

This milestone is:

- advisory-only
- deterministic
- append-only
- replay-visible
- governance-safe
- persistence-only

It does not introduce:

- execution authority
- worker dispatch
- orchestration
- provider activation
- autonomous cognition
- hidden continuation
- runtime cognition loops
- semantic reasoning
- governance mutation
- proposal repair
- automatic approval
- execution states

## CLI

The CLI command:

```bash
aigol moc append-ledger --persistence-record <record.json> --ledger-path <path> --json --output <path>
```

reads an explicit persistence record, validates append-only constraints, appends one canonical JSONL entry if valid, and optionally writes the resulting ledger entry artifact.

The command does not approve proposals, execute proposals, dispatch workers, activate providers, mutate prior ledger entries, mutate governance, auto-correct proposals, infer hidden state, or trigger approval automatically.
