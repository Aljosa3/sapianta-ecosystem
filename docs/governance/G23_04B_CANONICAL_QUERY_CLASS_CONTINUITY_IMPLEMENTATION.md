# G23-04B Canonical Query-Class Continuity Across Clarification

Status: completed

Date: 2026-07-12

## Objective

Preserve canonical Platform Core query identity across clarification without
introducing a subsystem, changing router ownership, or assigning semantic
authority to a Human Interface.

## Implemented Continuity

The existing replay-backed UHI clarification continuity path now resolves and
records query identity for:

- the original Human request;
- the clarification reply in isolation;
- the final clarification-resolved request.

For ordinary clarification, Platform Core routes an extended request containing
the original request, active clarification questions, and clarification answer.
The reply no longer replaces the original request at the governed read-only
routing boundary.

The existing single-route Unified Platform Query Router remains authoritative.
The continuity layer does not select a peer route or invoke multiple routes for
execution. It records deterministic identity evidence and supplies one final
resolved query to the existing read-only binding.

## Replay-Visible Evidence

The clarification continuity artifact records:

- original, clarification, and final query hashes;
- original, clarification, and final query classes;
- original, clarification, and final selected composition capabilities;
- whether query-class continuity was preserved;
- whether the reply explicitly changed intent;
- the deterministic continuity decision.

The enriched development intent also carries the final resolved query and
continuity decision into downstream Project Objective, conversation,
read-only routing, presentation, and workspace evidence.

## Intent Change and Fail-Closed Semantics

Explicit replacement language such as `instead`, `change my request to`, or
`replace the original request` causes deterministic reclassification from the
reply rather than preservation of the original class.

If the final class changes without an explicit intent-change declaration, the
continuity path fails closed: clarification remains required and approval,
runtime binding, and read-only binding are not admissible.

Existing governed work-type preservation remains authoritative and may impose
additional fail-closed constraints independently of query-class continuity.

## Architectural Ownership

- clarification satisfaction and continuity: Platform Core;
- query classification and single-route selection: Unified Platform Query
  Router;
- read-only composition: the existing selected Platform Core service;
- replay evidence: existing UHI clarification/workspace replay artifacts;
- Human Interface: transport and rendering only;
- Provider: no continuity authority;
- Worker: no continuity authority.

No change was made to `aicli`, Provider execution, Worker execution,
authorization ownership, governance mutation, or replay ownership.

## Regression Evidence

Regression coverage verifies:

- Architectural Certification remains bound to Architectural Meta Audit after
  a clarification reply whose standalone wording classifies as Platform
  Knowledge;
- original and final composition capability identity remain replay-visible;
- explicit intent replacement reclassifies to Development Composition
  Planning;
- historical clarification completion and replay continuity remain intact;
- historical router, Platform Knowledge, and planning behavior remain intact;
- Provider invocation remains false;
- Worker invocation remains false;
- repository mutation remains false.

## Validation

Validation performed:

- focused G23-04B, clarification, router, and Architectural Certification
  regressions: 34 passed;
- full regression suite: 6,005 passed, 4 skipped;
- governance conformance tests: 5 passed;
- governance conformance engine: deterministic, fail-closed, read-only, 18
  checks passed, 0 critical violations, status `PARTIALLY_CONFORMANT`;
- `py_compile`: passed;
- `git diff --check`: passed.

Known conformance hook drift remains visible and is not reframed as full
conformance.

## Deterministic Verdict

`CANONICAL_QUERY_CLASS_CONTINUITY_COMPLETED_WITHOUT_ARCHITECTURAL_OWNERSHIP_CHANGE`
