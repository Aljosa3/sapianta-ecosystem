# Platform Semantic Gap Closure G2-10 Command Boundary And Recommendation Prose Certification V1

Status: implementation governance artifact.

Scope: permanent architectural boundary certification between deterministic command
parsers and natural-language recommendation prose.

This batch does not change governance, OCS, PPP, approval, provider, worker, replay, or
execution authority. It does not retire compatibility layers.

## 1. Purpose

Batch G2-10 certifies that exact commands remain structured command authority outside
UBTR, while ambiguous recommendation prose can record CSA evidence only after deterministic
command parser non-match.

The migration is evidence-first. UBTR/CSA is not allowed to replace exact command
parsing, approve work, resume work, invoke providers, invoke workers, authorize execution,
or mutate replay.

## 2. Runtime Change

The recommendation approval and follow-up runtime now emits a hash-bound
`COMMAND_BOUNDARY_COMPARISON_ARTIFACT_V1` inside replay-visible approval and follow-up
artifacts.

The artifact records:

- command parser decision;
- CSA reference and hash when CSA lineage is supplied;
- fallback reason;
- semantic comparison hash;
- parity evidence;
- migration batch id;
- replay lineage;
- authority preservation flags.

## 3. Certified Command Boundaries

Certified exact command boundaries:

- recommendation approval commands;
- recommendation rejection commands;
- recommendation ignore commands;
- recommendation follow-up commands;
- approval-resume commands;
- proposal approval decisions;
- resume, retry, cancel, and lifecycle command families as structured command authority.

Exact parser matches remain authoritative. CSA is explicitly marked unused on exact command
matches even when CSA lineage is present.

## 4. CSA After Parser Non-Match

When deterministic recommendation follow-up parsing cannot establish an unambiguous
command match, the runtime can record CSA lineage as observational evidence.

This evidence is non-authoritative:

- it does not convert unsupported prose into an approved command;
- it does not create a follow-up candidate;
- it does not authorize implementation;
- it does not request execution;
- it does not invoke providers or workers.

Compatibility fallback remains authoritative for non-parity prose.

## 5. Replay Evidence

G2-10 replay-visible evidence records:

- `command_boundary_source`;
- `command_parser_decision`;
- `command_boundary_comparison_artifact`;
- `command_boundary_comparison_hash`;
- `command_boundary_parity_status`;
- `command_boundary_migration_batch_id`;
- `canonical_semantic_artifact_reference`;
- `canonical_semantic_artifact_hash`;
- `command_boundary_fallback_reason`.

Replay reconstruction exposes the same fields so later explanation, replay/hardening, and
compatibility retirement batches can consume structured command-vs-prose evidence.

## 6. Preserved Boundaries

G2-10 preserves:

- deterministic command parser authority;
- human approval authority;
- OCS cognition authority;
- PPP structured authority;
- governance authority;
- provider ownership;
- worker ownership;
- replay ownership;
- execution authorization boundaries;
- compatibility fallback.

UBTR remains a semantic provenance source only after parser non-match.

## 7. Regression Coverage

Regression coverage added:

- exact recommendation approval command remains parser-authoritative;
- CSA lineage is ignored on exact command match;
- unsupported recommendation prose records CSA evidence only after parser non-match;
- parser non-match remains fail-closed and non-authoritative;
- replay reconstruction exposes command-boundary comparison evidence;
- provider, worker, execution, implementation, governance, and replay authority remain
  unchanged.

Existing command-boundary coverage continues to certify approval resume, proposal
approval, recommendation approval/follow-up, and interactive command paths.

## 8. Rollback Impact

Rollback is bounded:

- exact command parser behavior is unchanged;
- compatibility fallback remains available for ambiguous prose;
- removing G2-10 evidence fields restores the previous replay surface without changing
  routing behavior;
- no state machine, approval, resume, provider, worker, execution, governance, or replay
  authority is transferred to UBTR.

## 9. Certification Impact

G2-10 certifies the permanent boundary between structured commands and natural-language
recommendation prose.

Certification proves that UBTR semantic authority does not absorb exact command authority,
while replay can still observe CSA evidence for ambiguous prose after deterministic parser
non-match.

## 10. Remaining Generation 2 Inventory

Remaining Generation 2 migration inventory after G2-10:

- explanation rendering migration;
- replay, hardening, and replay-derived classifiers;
- provider-assisted and legacy classifier closure;
- compatibility retirement certification.

## 11. Final Verdict

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_10_READY
```
