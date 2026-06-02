# UNIFIED_REPLAY_RECONSTRUCTION_FOUNDATION_V1

UNIFIED_REPLAY_RECONSTRUCTION_FOUNDATION_STATUS = READY_WITH_GAPS

## Purpose

Define the canonical reconstruction model that allows AiGOL to rebuild and inspect complete replay chains across:

- Conversation;
- Source Routing;
- Execution Lifecycle;
- Governed Learning Lifecycle;
- Learning-to-Execution Bridge;
- Worker Evidence;
- Replay Evidence.

This is review only. It does not implement runtime code, modify replay, modify governance, modify CLI behavior, create execution requests, dispatch workers, invoke workers, execute work, or self-apply improvements.

## 1. What Is A Canonical Chain?

A canonical chain is a replay-reconstructable lineage of related AiGOL artifacts that share one governed operational intent.

It may include:

```text
Human Prompt
-> Source Routing
-> Proposal
-> Approval
-> Execution Request
-> Ready For Dispatch
-> Worker Assignment
-> Dispatch
-> Invocation
-> Execution
-> Result
-> Completion
-> Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
-> Implementation Plan
-> Implementation-to-Execution Bridge
-> Execution Request
```

A canonical chain is not an authority source. It is a reconstruction view over replay evidence.

## 2. How Is A Chain Uniquely Identified?

The preferred identity is:

```text
canonical_chain_id
```

For chain-aware artifacts, `canonical_chain_id` is mandatory.

For earlier artifacts or compatibility paths that do not yet carry `canonical_chain_id`, reconstruction may use:

- human prompt reference;
- source router reference;
- proposal reference and hash;
- approval reference and hash;
- execution request reference and hash;
- replay reference;
- artifact hash;
- parent and child artifact references.

Compatibility reconstruction is allowed only as evidence classification. It may not pretend that a missing `canonical_chain_id` exists.

## 3. How Are Execution Chains Reconstructed?

Execution chains are reconstructed by locating an execution request and walking upstream and downstream evidence:

```text
Proposal
-> Proposal Approval
-> Execution Request
-> Ready For Dispatch
-> Worker Assignment
-> Dispatch
-> Invocation
-> Execution
-> Completion
-> Result
```

For each stage, reconstruction must validate:

- artifact type;
- artifact hash;
- replay wrapper hash;
- event ordering;
- upstream reference;
- upstream hash;
- lifecycle status;
- authority flags;
- non-mutation flags;
- canonical chain id when present.

## 4. How Are Learning Chains Reconstructed?

Learning chains are reconstructed from a result artifact and its downstream learning artifacts:

```text
Result
-> Result Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
-> Implementation Plan
```

Learning reconstruction must validate:

- result reference and hash;
- evaluation reference and hash;
- proposal reference and hash;
- review reference and hash;
- approval reference and hash;
- implementation plan reference and hash;
- same `canonical_chain_id`;
- human authorization for approval;
- no self-approval;
- no self-implementation;
- no governance or replay mutation.

## 5. How Are Bridge Chains Reconstructed?

Bridge chains are reconstructed from:

```text
Implementation Plan
-> IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1
-> source-aware EXECUTION_REQUEST_ARTIFACT_V1
```

Bridge reconstruction must validate:

- implementation plan reference and hash;
- improvement approval reference and hash;
- explicit human execution-request authorization reference;
- canonical chain id continuity;
- bridge link artifact hash;
- execution request artifact hash;
- non-dispatch, non-invocation, and non-execution flags.

## 6. How Are Replay Fragments Merged?

Replay fragments are merged by deterministic evidence joins:

1. `canonical_chain_id` exact match;
2. upstream reference and hash match;
3. replay reference match;
4. event ordering within each runtime replay directory;
5. artifact type expected by lifecycle model;
6. timestamp used only as secondary ordering evidence, never as identity authority.

Fragments must not be merged when:

- chain ids conflict;
- references mismatch;
- hashes mismatch;
- stage order is invalid;
- authority flags are introduced;
- unrelated prompt or proposal references share no replay-visible relationship.

## 7. How Is Chain Corruption Detected?

Chain corruption is detected when:

- artifact hash mismatch occurs;
- replay wrapper hash mismatch occurs;
- required artifact is missing;
- required reference is missing;
- upstream hash does not match referenced artifact;
- `canonical_chain_id` is missing where mandatory;
- chain ids conflict;
- lifecycle stage order is invalid;
- duplicate artifacts claim the same stage without a certified duplicate policy;
- replay event ordering is invalid;
- provider, worker, replay, or artifact claims unauthorized authority;
- a learning artifact attempts approval, implementation, execution request creation, dispatch, invocation, or execution outside its boundary.

Corruption must fail closed.

## 8. How Is Missing Evidence Detected?

Missing evidence is detected by stage requirements.

Each chain view has a required stage list:

- conversation chain;
- execution chain;
- learning chain;
- bridge chain;
- full chain lineage.

If a required stage is absent, reconstruction must return:

```text
RECONSTRUCTION_STATUS = INCOMPLETE
```

not:

```text
RECONSTRUCTION_STATUS = VALID
```

Replay may report missing evidence. Replay may not infer or repair it.

## 9. How Are Chain Boundaries Preserved?

Each reconstructed segment preserves its original authority boundary:

- conversation may answer but not execute;
- source routing selects source but does not approve;
- proposal proposes but does not execute;
- approval authorizes only its certified scope;
- execution request creates a candidate but does not dispatch;
- readiness validates but does not assign;
- worker assignment assigns but does not dispatch;
- dispatch dispatches but does not invoke;
- invocation invokes but does not complete;
- execution records execution start but does not certify results;
- completion records completion but does not evaluate quality;
- result captures output but does not approve improvement;
- evaluation observes but does not approve;
- improvement proposal proposes only;
- improvement review reviews only;
- improvement approval authorizes planning only;
- implementation plan plans only;
- bridge creates a request only with explicit human authorization.

## 10. Human Operator Inspection

Future CLI commands enabled by this model:

```text
AiGOL > show latest chain
AiGOL > inspect chain <CHAIN_ID>
AiGOL > show learning lifecycle
AiGOL > show execution lifecycle
AiGOL > explain chain lineage
AiGOL > reconstruct full chain
```

Required inspection views:

- latest chain;
- chain by id;
- learning chain;
- execution chain;
- bridge chain;
- full chain lineage;
- corruption report;
- missing evidence report;
- authority boundary report.

## 11. Constitutional Preservation

Unified reconstruction preserves:

```text
LLM proposes
AiGOL governs
Human authorizes
Worker executes
Replay records
```

Mapping:

| Role | Reconstruction meaning |
| --- | --- |
| LLM proposes | Provider evidence may appear as non-authoritative proposal or conversation evidence |
| AiGOL governs | AiGOL validates artifact lineage, chain continuity, and boundaries |
| Human authorizes | Approval and bridge authorization remain explicit evidence |
| Worker executes | Worker evidence is execution output only, not governance authority |
| Replay records | Replay reconstructs and reports without mutation or decision authority |

## 12. Mandatory Replay Evidence

Mandatory evidence depends on requested view.

Minimum full-chain evidence:

- human prompt replay or prompt reference;
- source router replay;
- proposal replay;
- proposal approval replay;
- execution request replay;
- ready-for-dispatch replay;
- worker assignment replay;
- dispatch replay where applicable;
- invocation replay where applicable;
- execution replay where applicable;
- completion replay where applicable;
- result replay;
- result evaluation replay;
- improvement proposal replay;
- improvement review replay;
- improvement approval replay;
- implementation plan replay;
- implementation-to-execution bridge replay;
- source-aware execution request replay;
- artifact hashes;
- replay wrapper hashes;
- human authorization evidence.

## Final Classification

```text
UNIFIED_REPLAY_RECONSTRUCTION_FOUNDATION_STATUS = READY_WITH_GAPS
```

The model is ready. Gaps remain because no unified reconstruction runtime or CLI command exists, and mixed-generation artifacts require compatibility reconstruction where `canonical_chain_id` is absent.
