# ACLI_PROPOSAL_CONTENT_FIDELITY_V1

Status: Ready

Scope: Governed development proposal content fidelity

Target verdict:

```text
ACLI_PROPOSAL_CONTENT_FIDELITY_READY
```

## 1. Purpose

This artifact defines how governed development proposals should preserve operator intent in proposal naming, target paths, and proposal previews while preserving replay determinism, approval binding, and fail-closed behavior.

It builds on `ACLI_PROPOSAL_CONTENT_AUDIT_V1`.

The goal is to make proposals understandable before approval without weakening governance.

## 2. Fidelity Principles

Proposal content fidelity means:

- explicit artifact names are preserved when deterministically safe;
- requested governance artifact identifiers are visible to the operator;
- generated fallback names remain available when extraction is ambiguous or unsafe;
- proposal previews show intended repository changes before approval;
- replay records how names, paths, and previews were derived;
- approval remains bound to the exact proposal hash;
- failure or ambiguity fails closed before mutation.

Fidelity does not mean accepting arbitrary natural language as a file path.

## 3. Proposal Naming Model

The proposal naming model should support three naming modes:

### 3.1 Requested Name Mode

Used when the operator supplies one deterministic, safe artifact identifier.

Example:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices.
```

Detected identifier:

```text
ACLI_USAGE_GUIDELINES_V1
```

Target path:

```text
docs/governance/ACLI_USAGE_GUIDELINES_V1.md
```

This mode preserves operator intent directly.

### 3.2 Generated Fallback Mode

Used when no safe identifier is present.

Target path remains deterministic:

```text
docs/governance/ACLI_GOVERNED_DEVELOPMENT_<SEED>_V1.md
```

This mode preserves replay determinism and safe proposal generation.

### 3.3 Ambiguous Name Fail-Closed Mode

Used when multiple possible artifact identifiers are present or the identifier is unsafe.

Examples:

```text
Create ACLI_USAGE_GUIDELINES_V1 and ACLI_OPERATOR_GUIDE_V1.
Create governance artifact ../unsafe.
Create artifact ACLI USAGE GUIDELINES.
```

Behavior:

- do not pick a name silently;
- do not mutate;
- ask the operator to clarify the intended artifact name;
- replay the ambiguity and clarification request.

## 4. Safe Identifier Requirements

A requested governance artifact identifier is deterministically safe only when it satisfies all requirements:

- uppercase letters, digits, and underscores only;
- begins with an uppercase letter;
- ends with `_V<integer>`;
- contains no path separator;
- contains no dot;
- contains no whitespace;
- contains no shell metacharacters;
- maps only to an allowed governance directory;
- exactly one identifier is detected for the artifact target.

Recommended pattern:

```text
\b[A-Z][A-Z0-9_]*_V[0-9]+\b
```

This pattern is intentionally conservative.

## 5. Target Path Generation

Target path generation must be deterministic.

Allowed requested-name target path:

```text
docs/governance/<REQUESTED_ARTIFACT_NAME>.md
```

Allowed fallback target path:

```text
docs/governance/ACLI_GOVERNED_DEVELOPMENT_<SEED>_V1.md
```

Target path generation must reject:

- absolute paths;
- parent directory traversal;
- nested arbitrary paths from user prompt;
- hidden files;
- file extensions other than `.md` for governance artifacts;
- paths outside allowlisted directories.

## 6. Proposal Previews

Pre-approval proposal previews should show intended repository changes before approval.

Required preview fields:

- requested artifact name, if detected;
- selected artifact name;
- selected target path;
- whether the target was requested or generated;
- artifact purpose;
- proposed content section summary;
- repository mutation paths;
- mutation operations;
- validation command;
- replay reference;
- proposal hash.

Example preview:

```text
Proposal preview

Requested artifact:
ACLI_USAGE_GUIDELINES_V1

File ACLI plans to create:
docs/governance/ACLI_USAGE_GUIDELINES_V1.md

Purpose:
Document recommended operator practices for using ACLI as the primary development interface.

Content sections:
- Status
- Purpose
- Boundaries

Additional repository changes:
- aigol/runtime/acli_governed_development_<seed>.py

Validation:
git diff --check
```

Preview rendering must not mutate files and must not authorize execution.

## 7. Proposal Content Fidelity

Governance artifact content should preserve:

- requested artifact title;
- operator-stated purpose;
- original human request;
- governance boundaries;
- approval requirement;
- replay source statement.

When a requested name is safe, the generated content title should use it:

```text
# ACLI_USAGE_GUIDELINES_V1
```

When no requested name is safe, fallback content title should use the generated deterministic name.

The original human request must always be preserved in the proposal artifact.

## 8. Replay Impact

Replay must record the full naming decision.

Required replay fields:

```text
requested_artifact_identifier
requested_identifier_detected
requested_identifier_detection_rule
requested_identifier_safe
requested_identifier_ambiguity
selected_artifact_identifier
selected_target_path
target_path_mode
fallback_seed
collision_status
collision_resolution
proposal_preview_hash
proposal_hash
approval_binding_hash
```

Allowed `target_path_mode` values:

```text
REQUESTED_IDENTIFIER
GENERATED_FALLBACK
AMBIGUOUS_FAIL_CLOSED
UNSAFE_FAIL_CLOSED
COLLISION_FAIL_CLOSED
```

Replay reconstruction must verify:

- selected target path matches the recorded mode;
- requested identifier was safe before use;
- fallback seed matches deterministic input;
- proposal preview hash matches rendered preview;
- approval hash binds to the final proposal artifact;
- mutation did not occur before approval.

## 9. Approval Binding

Approval must bind to the exact proposal artifact after name and path selection.

Changing any of the following requires a new proposal and new approval:

- selected artifact identifier;
- selected target path;
- proposed content;
- repository mutation list;
- validation command;
- replay references;
- proposal preview content.

The approval artifact must include the proposal hash produced after content fidelity decisions are complete.

## 10. Collision Handling

Collision handling must be deterministic and fail closed unless a governed overwrite policy exists.

Collision types:

- target file already exists;
- target path is staged for another mutation;
- target path conflicts with generated fallback;
- requested target conflicts with non-governance file;
- multiple proposed mutations target the same path.

Recommended default:

```text
COLLISION_FAIL_CLOSED
```

Operator-facing message:

```text
ACLI detected that the requested target already exists or conflicts with another proposal.

No changes were made.

Please clarify whether you want to update the existing artifact or choose a different artifact name.
```

Replay must record:

- collision path;
- collision type;
- repository context hash;
- fail-closed decision;
- operator clarification request.

## 11. Fail-Closed Requirements

The proposal path must fail closed when:

- requested identifier is unsafe;
- multiple identifiers are ambiguous;
- target path escapes allowlisted directories;
- collision policy is missing;
- preview cannot be rendered;
- proposal hash cannot be computed;
- approval binding cannot include the final proposal hash;
- replay cannot record naming decision evidence.

Fail-closed behavior must occur before mutation.

## 12. Implementation Options

### Option A: Preview Only

Render current proposal content more clearly without changing target path generation.

Benefits:

- lowest risk;
- no mutation behavior change;
- immediate operator comprehension improvement.

Limitations:

- requested artifact names remain informational only;
- generated hash-based names remain actual targets.

### Option B: Requested Name Detection With Informational Preview

Detect safe artifact identifiers and show them in proposal preview, but keep generated target paths.

Benefits:

- proves deterministic extraction;
- improves operator understanding;
- avoids changing mutation target behavior.

Limitations:

- operator still sees mismatch between requested name and generated target.

### Option C: Requested Name Targeting

Use safe requested identifiers as actual governance artifact targets.

Benefits:

- highest operator fidelity;
- target path matches request;
- proposal preview becomes intuitive.

Required safeguards:

- strict identifier validation;
- target path allowlist;
- collision fail-closed handling;
- replay of naming decision;
- approval binding after path selection;
- regression tests for safe, missing, ambiguous, unsafe, and collision cases.

### Option D: Provider-Assisted Purpose Summary

Use provider assistance only to summarize purpose text after deterministic target selection.

This must remain non-authoritative and replay-visible. It must not select names or target paths.

## 13. Recommended Path

Recommended implementation sequence:

1. Implement proposal preview rendering from existing proposal artifacts.
2. Add deterministic identifier extraction and replay evidence.
3. Add informational requested-name preview.
4. Add requested-name target path generation behind strict fail-closed validation.
5. Add collision fail-closed handling.
6. Add approval binding regression tests.

This sequence improves operator understanding first, then introduces target fidelity under bounded safeguards.

## 14. Validation Requirements

Validation must cover:

- explicit safe artifact name preserved;
- requested governance artifact identifier recorded in replay;
- safe target path generated;
- missing name falls back to generated deterministic name;
- ambiguous names fail closed;
- unsafe names fail closed;
- existing target collision fails closed;
- proposal preview renders before approval;
- proposal hash changes when selected name or content changes;
- approval binds to final proposal hash;
- no mutation occurs before approval;
- replay reconstructs naming decision.

## 15. Non-Goals

This artifact does not:

- implement extraction;
- change runtime behavior by itself;
- authorize provider selection of names;
- allow arbitrary user paths;
- permit mutation without approval;
- weaken replay determinism;
- bypass collision handling;
- redesign governed development.

## 16. Final Verdict

Proposal content fidelity is ready as a bounded design.

Explicit artifact names may be preserved when deterministically safe. Generated hash names remain the safe fallback. Proposal previews should expose intended repository changes before approval. Replay must record every naming decision, target path decision, collision decision, preview hash, and approval binding.

```text
ACLI_PROPOSAL_CONTENT_FIDELITY_READY
```
