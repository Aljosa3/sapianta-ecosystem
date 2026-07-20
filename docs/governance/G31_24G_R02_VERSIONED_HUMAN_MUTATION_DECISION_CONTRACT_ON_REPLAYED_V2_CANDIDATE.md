# G31-24G-R02 — Versioned Human Mutation Decision Contract on Replayed V2 Candidate

## Baseline and verdict

Baseline branch: `master`.

Baseline HEAD: `ba787435b2a6bd04b5e892b55d600519ca070053` (`feat(governance): bind accepted result to replayed candidate`).

The committed baseline reports are tracked.  The R01 report contains the required committed verdict:

`G31_V2_ACCEPTED_RESULT_TO_EXISTING_FILE_CANDIDATE_PROVENANCE_BINDING_OPERATIONAL`

Implementation verdict:

`G31_V3_HUMAN_MUTATION_DECISION_CONTRACT_ON_REPLAYED_V2_CANDIDATE_OPERATIONAL`

Plain-language conclusion: a human can now record one explicit, replay-bound `APPROVED` or `REJECTED` decision over one reconstructed V2 `REPLACE_CONTENT` candidate.  This is evidence for a later authorization request only.  It neither authorizes nor performs a repository mutation.

## Bounded implementation

Production change: `aigol/runtime/human_decision_runtime.py` only (224 added lines; no production module added).  AiCLI was intentionally not extended: the prompt permits, but does not require, transport binding, and no existing caller can make an authorization or mutation reachable through this owner.

Focused test: `tests/test_g31_24g_r02_human_mutation_decision.py`.

New public symbols:

- `prepare_existing_file_mutation_decision_context`
- `record_existing_file_mutation_decision`
- `reconstruct_existing_file_mutation_decision_replay`
- `render_existing_file_mutation_decision_context`
- `render_existing_file_mutation_decision`

The existing V1 generic decision and V2 content-acceptance construction, vocabulary, hashing, Replay, reconstruction, rendering, and callers are unchanged.

## V3 contract and authority

The existing human-decision owner now supplies V3 constants and artifacts:

```text
decision_type  = MUTATION_AUTHORIZATION
decision_scope = EXISTING_FILE_REPLACE_ONLY
decision_outcome = APPROVED | REJECTED
HUMAN_DECISION_ARTIFACT_V3
HUMAN_DECISION_RETURNED_V3
```

The V3 subject is created only by reconstructing the existing public G31 V2 candidate Replay and validating its V2 artifact.  Its binding hash includes candidate identity/hash, candidate Replay reference/hash, candidate-provenance binding hash, actor identity, and the complete candidate provenance.  That provenance already binds session, repository identity/root/grounding, accepted result and acceptance, content decision, prerequisite, manifest, V2 `REPLACE_CONTENT`, target, raw preimage/postimage hashes, content hashes, source/replacement modes, and content/test/disposable validation evidence.

The decision and returned artifacts repeat the candidate identity, hash, Replay hash, and provenance-binding hash.  No generic V1 normalization is used.  `APPROVE`, `YES`, `SATISFIED`, `ACCEPTED`, booleans, content-acceptance vocabulary, and free text fail closed before recording.

Content acceptance, this distinct human decision, mutation authorization, and repository mutation remain separate authority owners.  AiCLI remains non-authoritative.  CODEX remains a Worker-role resource and Provider authority remains absent.

## Replay and presentation

The V3 human-decision owner owns a standalone immutable four-wrapper Replay:

```text
000 mutation_decision_context_presented
001 mutation_decision_request_recorded
002 mutation_decision_recorded
003 mutation_decision_returned
```

Reconstruction verifies wrapper hashes/order, session containment, artifact version/type, exact actor, exact candidate and candidate Replay, provenance binding, outcome, and authority flags.  The owner rejects existing wrapper destinations and scans the session for an already-recorded decision consuming the same candidate hash.

Presentation identifies target, `REPLACE_CONTENT`, preimage/postimage, the distinction from content acceptance, the fact that approval permits only a later authorization request, and that no repository file changes in this generation.

## Stop states and unreachable transitions

For `APPROVED`:

```text
mutation_decision_recorded = true
mutation_decision_approved = true
mutation_authorized = false
main_repository_mutated = false
```

For `REJECTED`, the same fields hold except `mutation_decision_approved = false`.

Both context and decision artifacts explicitly retain false execution, Worker, Provider, command, patch, authorization, and mutation flags.  The changed owner imports only the existing candidate validator/reconstructor and serialization support.  It has no production caller yet, and contains no authorization-owner, mutation-owner, Worker, Provider, command-runner, or source-write call.

## Validation

Passed:

- `python -m py_compile aigol/runtime/human_decision_runtime.py tests/test_g31_24g_r02_human_mutation_decision.py`
- `python -m pytest -q -rA tests/test_g31_24g_r02_human_mutation_decision.py` — 3 passed.
- `python -m pytest -q -rA tests/test_human_decision_runtime_v1.py` — 7 passed.
- `python -m pytest -q -rA tests/test_g31_24e_human_content_acceptance_to_existing_acceptance_binding.py` — 4 passed in 374.82s.
- `python -m pytest -q -rA tests/test_governance_conformance.py` — 5 passed.
- `python -m pytest -q -rA tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py` — 12 passed.
- `python -m runtime.governance.governance_conformance_engine` — deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`: 18 checks passed, 2 pre-existing hook mismatches, 0 critical violations.
- Parent and all three nested repositories: `git diff --check` passed; nested statuses were clean.

The R01 candidate suite was run once and failed before candidate construction in its existing full conversational fixture: all 3 cases raised `KeyError: 'lineage'` at `runtime_result['codex_worker_activation_capture']['lineage']['grounding']` (also reached by the existing AiCLI candidate transport edge).  This occurred with no V3 caller and no source-repository mutation; it is recorded as a baseline-fixture/runtime-evidence failure, not masked as V3 success.

No long PTY workflow was run.  All V3 fixture Replay writes were under pytest temporary directories.  No authorization, repository mutator, Worker, Provider, command runner, patch owner, or source-repository write was invoked by V3 tests.

## Governance and next state

The next transition remains bounded and separate: connect the V3 decision only to a later canonical mutation-authorization request after resolving the existing R01 fixture lineage failure.  Do not connect it directly to mutation.

Next state:

`G31_24G_R02_HUMAN_MUTATION_DECISION_RECORDED_AUTHORIZATION_BINDING_REQUIRED`
