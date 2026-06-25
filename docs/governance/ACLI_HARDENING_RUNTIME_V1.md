# ACLI_HARDENING_RUNTIME_V1

Status: READY

Target verdict:

```text
ACLI_HARDENING_RUNTIME_READY
```

## 1. Runtime Purpose

`ACLI_HARDENING_RUNTIME_V1` turns normal completed ACLI interactions into structured Platform Core Generation 1 hardening evidence.

The operator does not need to manually execute predefined hardening scenarios. Instead, each completed interaction can be submitted to the hardening runtime, which records what was exercised, whether the interaction passed, which issues were observed, and how the interaction contributes to production hardening coverage.

This runtime is observational and evidence-generating only.

It does not:

- select workflows;
- approve execution;
- dispatch workers;
- mutate governance;
- mutate replay;
- change ACLI behavior;
- close issues without regression evidence.

## 2. Runtime Inputs

Required inputs:

- `hardening_id`;
- `interaction_id`;
- completed ACLI interaction evidence;
- `created_at`;
- hardening replay directory.

Optional inputs:

- operator feedback;
- prior hardening state.

Completed ACLI interaction evidence may include:

- natural-language prompt;
- workflow selection;
- runtime path;
- Human -> Governance translation evidence;
- Governance -> Human explanation evidence;
- proposal evidence;
- approval, rejection, or modification evidence;
- worker dispatch evidence;
- validation evidence;
- replay reference;
- replay hash;
- provider fallback or escalation evidence;
- ERR evidence.

Malformed interaction input fails closed before any hardening replay artifact is written.

## 3. Automatic Scenario Detection

The runtime detects exercised scenario categories from completed interaction evidence.

Supported scenario categories:

- Human -> Governance Translation;
- Governance -> Human Translation;
- HIRR;
- Routing;
- Proposal Generation;
- Proposal Preview;
- Approval;
- Reject;
- Request Modification;
- Replay;
- Resume;
- Explanation;
- LLM-assisted Explanation;
- Provider Escalation;
- Worker Dispatch;
- Validation;
- ERR;
- Replay Review.

Scenario detection is deterministic and evidence-based. Unknown interactions are classified as `UNKNOWN` rather than inferred into a passing scenario.

## 4. Automatic Validation

Each hardening event receives one result:

```text
PASS
PARTIAL PASS
FAIL
UNKNOWN
```

Result classification is based on:

- replay evidence presence;
- authority boundary status;
- approval boundary status;
- execution and worker evidence;
- validation evidence;
- provider and worker availability;
- fail-closed behavior;
- operator feedback;
- detected issue severity.

P0 issues produce `FAIL`.

P1 issues produce `PARTIAL PASS`.

P2 and P3 issues remain visible without automatically blocking production readiness.

## 5. Operator Feedback

The runtime generates an optional feedback prompt:

```text
Was everything understandable?
```

Supported choices:

- Very Clear;
- Mostly Clear;
- Somewhat Confusing;
- Confusing.

Optional free-text feedback is supported.

Feedback is recorded as hardening evidence. Confusing feedback creates a UX issue for review.

## 6. Issue Tracking

The runtime automatically detects and records issues across:

- UX;
- routing;
- replay;
- approval;
- translation;
- worker;
- provider;
- performance;
- security;
- documentation;
- architecture;
- validation;
- ERR.

Every issue records:

- unique issue identifier;
- category;
- severity;
- replay reference;
- root-cause status;
- fix status;
- regression status;
- regression identifier.

Issue closure remains governed by the hardening program. The runtime does not close issues and does not treat an issue as resolved without regression evidence.

## 7. Coverage Metrics

The runtime continuously calculates:

- scenario coverage;
- workflow coverage;
- contract coverage;
- replay coverage;
- translation coverage;
- approval coverage;
- provider coverage;
- worker coverage;
- regression coverage;
- Generation 1 coverage.

Coverage is reconstructable from persisted hardening evidence and prior hardening state.

## 8. Production Readiness Metrics

The runtime calculates:

- Platform Core Hardening Score;
- Operator Experience Score;
- Production Readiness Score;
- open critical issues;
- open major issues;
- open minor issues;
- production blockers.

Scores are deterministic and replay-visible. Scores do not override human authority or production certification governance.

## 9. Dashboards

The runtime produces dashboard data for:

- Platform Hardening Progress;
- Scenario Coverage;
- Most Frequent Operator Problems;
- Remaining Production Blockers.

Dashboard output is read-only and derived from hardening evidence. It never creates approval, dispatch, execution, or governance mutation authority.

## 10. Replay Requirements

Hardening evidence is persisted as immutable replay-visible JSON.

Replay requirements:

- stable canonical hashes;
- wrapper replay hash;
- nested artifact hash;
- artifact type verification;
- authority flag verification;
- tamper detection;
- fail-closed reconstruction.

Replay reconstruction fails closed if:

- replay ordering is invalid;
- wrapper hash is invalid;
- artifact hash is invalid;
- artifact type is unexpected;
- authority flags are modified.

## 11. Authority Boundaries

The hardening runtime is non-authoritative.

It records:

- what happened;
- what evidence exists;
- what issue may exist;
- what coverage changed.

It never authorizes:

- execution;
- dispatch;
- worker invocation;
- provider invocation;
- governance mutation;
- replay mutation;
- lifecycle modification;
- approval creation.

Preserved invariant:

```text
Human = Authority
Replay = Source Of Truth

LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## 12. Runtime Interfaces

Implemented runtime module:

```text
aigol/runtime/acli_hardening_runtime.py
```

Primary functions:

```text
record_acli_hardening_interaction(...)
reconstruct_acli_hardening_replay(...)
render_platform_hardening_progress(...)
```

Focused tests:

```text
tests/test_acli_hardening_runtime_v1.py
```

## 13. Validation Evidence

Validation expectations:

```text
python -m pytest tests/test_acli_hardening_runtime_v1.py -q
python -m py_compile aigol/runtime/acli_hardening_runtime.py tests/test_acli_hardening_runtime_v1.py
git diff --check
```

The focused test suite verifies:

- PASS classification for completed governed development evidence;
- rejection without execution;
- request modification without execution;
- P0 failure when executed interaction lacks replay reference;
- provider unavailable partial pass;
- worker unavailable partial pass;
- UX feedback issue capture;
- cumulative statistics and dashboards;
- replay reconstruction;
- tamper fail-closed behavior;
- malformed input fail-closed behavior;
- stable artifact hashing.

## 14. Final Verdict

`ACLI_HARDENING_RUNTIME_V1` is ready as a passive, replay-safe runtime for converting normal ACLI usage into structured Platform Core Generation 1 hardening evidence.

Final verdict:

```text
ACLI_HARDENING_RUNTIME_READY
```
