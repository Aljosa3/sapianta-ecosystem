# GOVERNED_DEVELOPMENT_END_TO_END_CERTIFICATION_V1

Status: Executable Certification Artifact

Scope: End-to-end certification of natural-language ACLI governed development.

This artifact defines the executable certification path for:

```text
Natural Language
-> HIRR
-> DEVELOPMENT_INTENT
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> Governance Artifact Creation
-> Governed Repository Mutation
-> Validation
-> Replay
```

## 1. Certification Purpose

This certification exists to prove that ACLI can accept a natural development request, resolve it through HIRR, select the existing governed development workflow, execute the governed component workflows, preserve approval and proposal hash binding, validate through allowlisted commands, and reconstruct replay evidence.

The certification does not create a new workflow family.

## 2. Certification Entry Point

The certified entry point is natural language routed through `aigol conversation`.

Representative certified input:

```text
Add replay validation
```

Expected HIRR result:

```text
DEVELOPMENT_INTENT
```

Expected workflow selection:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

## 3. Required Evidence

Certification requires executable evidence for:

- conversational routing replay
- HIRR `DEVELOPMENT_INTENT` classification
- governed development proposal
- human approval artifact
- proposal hash binding
- governance artifact creation replay
- repository mutation worker replay
- validation command replay
- governed development workflow replay reconstruction
- fail-closed execution without valid approval
- fail-closed execution after post-approval proposal tampering

## 4. Approval Binding Requirements

The top-level governed development approval must bind:

- top-level proposal hash
- governance artifact component proposal hash
- repository mutation component proposal hash
- approved component order
- human approval authority

Execution must fail closed when approval is missing or no longer matches the proposal.

## 5. Proposal Hash Binding Requirements

The proposal must remain hash-bound from approval through execution.

Any post-approval proposal mutation must produce:

```text
FAILED_CLOSED
```

and must not create governance artifacts or repository mutations.

## 6. Repository Mutation Requirements

Repository mutation must execute only through the existing governed repository mutation runtime and repository mutation worker path.

The certification must verify:

- repository mutation worker used
- approved target paths preserved
- mutation performed only after approval
- worker protections preserved
- forbidden governance and replay paths remain protected by existing runtime checks

## 7. Validation Requirements

Validation must execute through the allowlisted validation command runner.

The certification requires:

```bash
git diff --check
```

Validation evidence must prove:

- command status completed
- allowlist enforced
- arbitrary shell execution prevented
- replay lineage preserved

## 8. Replay Requirements

Replay reconstruction must succeed for:

- ACLI conversational routing
- governed development workflow
- governance artifact creation component
- governed repository mutation component
- component validation commands

Replay is the source of truth for certification evidence.

## 9. Fail-Closed Requirements

Certification must verify fail-closed behavior for:

- missing approval
- proposal hash mismatch after approval

Both cases must preserve:

- no approval bypass
- no unauthorized repository mutation
- no uncontrolled execution
- replay-visible failure outcome

## 10. Executable Test

Canonical executable certification test:

```text
tests/test_governed_development_end_to_end_certification_v1.py
```

Required validation:

```bash
python -m pytest tests/test_governed_development_end_to_end_certification_v1.py
python -m pytest tests/test_governed_development_workflow_runtime_v1.py
python -m pytest tests/test_conversational_cli_runtime_v1.py -k "natural_development_intent or governed_development_workflow"
git diff --check
```

## 11. Identified Gaps

No new workflow-family gap is identified by this certification artifact.

Certification remains executable-evidence dependent: the verdict is valid only when the canonical certification tests and validation commands pass.

## 12. Final Verdict

```text
GOVERNED_DEVELOPMENT_END_TO_END_CERTIFIED
```
