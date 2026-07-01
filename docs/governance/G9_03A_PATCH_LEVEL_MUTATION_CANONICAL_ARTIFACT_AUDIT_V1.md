# G9-03A Patch-Level Mutation Canonical Artifact Audit V1

Status: patch-level mutation canonical artifact model audited.

Final verdict: PATCH_LEVEL_MUTATION_IS_INTENT_ONLY_CANONICAL_ARTIFACT_PRESERVED

## 1. Executive Summary

Patch-level mutation is compatible with AiGOL's certified canonical artifact model only if "patch-level" describes the human-facing request and deterministic mutation specification, not the final persisted execution artifact.

The canonical execution artifact remains the complete resulting file.

The correct model is:

```text
Human Intent
-> Patch Specification
-> Platform Core
-> Worker Platform
-> Complete Canonical File
-> Validation
-> Replay
```

The incorrect model is:

```text
Human Intent
-> Patch
-> Worker
-> Line-level mutation
-> Replay
```

G9-03 therefore remains architecturally valid when interpreted as:

- patch specification expresses the requested semantic change;
- Worker Platform deterministically constructs the complete resulting file before write;
- Replay records the patch specification, pre-state evidence, post-state evidence, and complete canonical post-mutation artifact reference;
- validation operates on the complete resulting artifact;
- hashes, certification, reconstruction, rollback, Platform Digital Twin, and Architectural Health remain artifact-based.

No new subsystem, authority layer, or patch engine authority is required.

## 2. Historical Architectural Review

AiGOL's prior generations consistently prefer deterministic canonical artifacts over incremental opaque deltas.

| Generation | Relevant Principle | Effect On Patch-Level Mutation |
| --- | --- | --- |
| Generation 6 | Platform Digital Twin and canonical projections emerge from certified Platform Core source records. | Mutation evidence must reconstruct complete state, not only a delta. |
| Generation 7 | Source records, projection envelopes, reconstruction manifests, hashes, statuses, and conflicts are canonicalized. | Patch evidence must fit deterministic source and projection models. |
| Generation 8 | Existing-file mutation is hash-bound and full-artifact oriented. | Patch-level editing must extend full-file replacement without weakening artifact reconstruction. |
| Generation 9 | Platform evolution methodology requires reuse, projection analysis, minimal canonicalization, implementation review, and certification. | Patch-level mutation should reuse artifact-based mutation and only canonicalize the patch request shape if needed. |

The historical model is:

```text
artifact state before mutation
-> governed transformation request
-> artifact state after mutation
-> replay-visible reconstruction evidence
```

It is not:

```text
unbounded line edit
-> mutable local state
-> replay stores only the line edit
```

## 3. Canonical Artifact Analysis

Patch-level editing introduces a smaller human-facing mutation expression, but it does not change the canonical artifact unit.

Canonical units:

| Layer | Canonical Unit | Authority Meaning |
| --- | --- | --- |
| Human request | Patch intent | Human-facing expression only. |
| OCS candidate | Deterministic patch specification plus expected complete post-file hash. | Proposal artifact, not execution authority. |
| Governance authorization | Hash-bound approval of candidate and exact resulting artifact hash. | Authorization evidence. |
| Worker execution | Deterministic construction of complete resulting file. | Execution evidence. |
| Replay | Pre-file hash, patch specification, complete post-file hash, rollback metadata, validation evidence. | Reconstruction evidence. |
| Validation | Complete resulting file and repository state within authorized scope. | Reproducibility evidence. |
| Platform Digital Twin | Source records and projection over complete certified evidence. | Non-authoritative projection. |

The patch specification is therefore a canonical request artifact, but not the canonical execution artifact.

The canonical execution artifact is:

```text
the complete resulting file content and its post-mutation hash
```

G9-03 should be read as requiring the Worker to construct the full resulting content from:

- approved pre-file content;
- approved old text block;
- approved new text block;
- exactly-once context match;
- approved expected post-hash.

The Worker may then write only the resulting complete file content, not persist a line-level mutation as the final state.

## 4. Replay Implications

Replay determinism is preserved only if Replay can reconstruct the complete before-and-after artifact state.

Replay must record or reference:

- target relative path;
- pre-mutation full-file hash;
- pre-mutation artifact reference where allowed by retention policy;
- exact patch specification;
- old text hash;
- new text hash;
- expected complete post-file hash;
- actual complete post-file hash;
- Worker execution artifact;
- rollback metadata;
- validation evidence;
- fail-closed conflict evidence when applicable.

Replay may include the textual patch as evidence of intent and transformation, but it must not rely on patch text alone as the persisted execution artifact.

Missing complete post-artifact hash or reconstruction reference must block completion claims.

Replay remains the reconstruction authority. A patch Worker must not become a replay reconstruction engine.

## 5. Governance Implications

Governance must authorize the exact mutation candidate and the expected complete artifact outcome.

Governance authorization must bind:

- candidate id;
- candidate hash;
- target path;
- pre-file hash;
- old text hash;
- new text hash;
- expected complete post-file hash;
- rollback metadata hash;
- authorized Worker id or Worker family;
- approval hash;
- replay reference.

Governance should not authorize a patch merely as a free-floating delta. The authorization is admissible only when the patch candidate deterministically implies a complete resulting artifact.

Certification remains artifact-based:

```text
approved candidate + authorized Worker + complete post-hash + Replay evidence + validation status
```

not:

```text
approved line change only
```

## 6. Worker Platform Implications

Worker Platform performs patch application only as deterministic artifact construction.

Required Worker behavior:

1. Read the complete current file.
2. Verify the complete current file hash equals the authorized pre-hash.
3. Verify the old text block occurs exactly once.
4. Construct the complete resulting file content in memory or equivalent deterministic buffer.
5. Verify the constructed complete resulting file hash equals the authorized expected post-hash.
6. Write the complete resulting file content.
7. Re-read or re-hash the written file.
8. Emit execution evidence.

The Worker must not:

- treat a patch as an authority;
- persist only a line-level delta as the execution artifact;
- use fuzzy matching;
- use regex replacement;
- repair conflicts;
- choose a different resulting artifact;
- validate success without the complete post-file hash;
- bypass Replay evidence.

This preserves Worker Platform's execution-only boundary.

## 7. Platform Digital Twin Implications

The Platform Digital Twin requires reconstructable state across certified source records, final verdicts, ownership records, replay evidence, and extension lineage.

Patch-only persistence would weaken the Digital Twin because a future projection would have to replay line deltas against uncertain or missing pre-state. That would create avoidable ambiguity and could make the patch engine a hidden reconstruction authority.

Complete canonical artifact persistence preserves Digital Twin compatibility:

- source records remain deterministic;
- projection envelopes can cite complete artifact hashes;
- ownership remains visible;
- reconstruction manifests can include before and after artifact references;
- conflicts remain explicit;
- certification history stays traceable.

Architectural Health also remains a deterministic projection because it can assess whether the mutation preserved ownership, replay, validation, and artifact continuity.

## 8. Rollback Model Implications

Rollback must remain artifact-based.

Rollback metadata should include:

- complete pre-mutation artifact hash;
- complete post-mutation artifact hash;
- inverse patch specification if useful;
- full pre-mutation content reference where retention policy allows;
- target path;
- authorization reference;
- execution reference;
- replay references.

The inverse patch is a convenience expression. It is not sufficient rollback authority by itself.

Rollback execution, when later certified, should restore or reconstruct the complete prior artifact under Governance authorization and Replay evidence.

## 9. Validation Implications

Validation must operate on complete artifacts.

For patch-level mutation, validation should evaluate:

- the complete resulting file;
- the authorized repository state visible to the validation Worker;
- the expected post-hash;
- any validation plan required by OCS and Governance.

Validation must not certify a patch merely because the textual delta was applied. It must validate the post-mutation artifact state.

This preserves validation reproducibility and avoids treating line-level edits as standalone executable evidence.

## 10. Implementation Recommendation

G9-03 should proceed to implementation only with the following interpretation:

```text
Patch-level mutation is intent-level and candidate-level.
Canonical mutation evidence remains complete-artifact-level.
```

Implementation should require:

- deterministic patch candidate schema;
- exact old text and new text;
- exactly-once context matching;
- complete pre-file hash;
- complete expected post-file hash;
- Worker construction of the complete resulting file before write;
- Replay evidence for patch specification and complete resulting artifact;
- rollback metadata tied to complete artifacts;
- validation against complete artifact state.

No new Platform Core subsystem is required.

No new patch engine authority is allowed.

No weakening of Replay determinism, Governance certification, Platform Digital Twin reconstruction, rollback reproducibility, or Architectural Health projection is acceptable.

## 11. Final Determination

Patch-level mutation is compatible with the certified AiGOL canonical artifact model when patch-level semantics remain limited to human intent and deterministic candidate specification.

The persisted execution evidence must remain complete-artifact based.

Final verdict: PATCH_LEVEL_MUTATION_IS_INTENT_ONLY_CANONICAL_ARTIFACT_PRESERVED

## 12. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: PATCH_LEVEL_MUTATION_IS_INTENT_ONLY_CANONICAL_ARTIFACT_PRESERVED
