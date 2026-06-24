# ACLI_PROPOSAL_CONTENT_FIDELITY_IMPLEMENTATION_V1

Status: Implemented

Scope: Governed development proposal content fidelity implementation

Target verdict:

```text
ACLI_PROPOSAL_CONTENT_FIDELITY_IMPLEMENTED
```

## 1. Purpose

This artifact records implementation of `ACLI_PROPOSAL_CONTENT_FIDELITY_V1`.

The implementation makes governed development proposals preserve explicit operator-provided governance artifact identifiers when deterministically safe, while preserving deterministic fallback naming, approval binding, replay determinism, collision handling, and fail-closed behavior.

## 2. Modified Files

Runtime modified:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
```

Tests modified:

```text
tests/test_acli_governed_development_execution_bridge_v1.py
```

Governance artifact added:

```text
docs/governance/ACLI_PROPOSAL_CONTENT_FIDELITY_IMPLEMENTATION_V1.md
```

## 3. Implemented Behavior

### 3.1 Deterministic Artifact Identifier Extraction

The bridge now detects explicit governance artifact identifiers using a conservative deterministic pattern:

```text
\b[A-Z][A-Z0-9_]*_V[0-9]+\b
```

Example:

```text
ACLI_USAGE_GUIDELINES_V1
```

When exactly one safe identifier is detected, the governed development proposal uses it as the governance artifact title and target filename.

### 3.2 Requested Target Path Generation

Safe requested identifiers generate target paths in the governance directory:

```text
docs/governance/<REQUESTED_ARTIFACT_IDENTIFIER>.md
```

Example:

```text
docs/governance/ACLI_USAGE_GUIDELINES_V1.md
```

### 3.3 Deterministic Fallback Naming

When no safe explicit identifier exists, the bridge preserves the existing deterministic fallback naming:

```text
ACLI_GOVERNED_DEVELOPMENT_<SEED>_V1
```

This preserves existing governed development behavior for general prompts such as:

```text
Add replay validation
```

### 3.4 Collision Handling

If a safe requested governance target already exists, proposal generation fails closed before approval or mutation.

The operator sees a fail-closed reason indicating the target path collision.

No worker runs.

No repository mutation occurs.

### 3.5 Proposal Preview

Pre-approval proposal summaries now show:

- requested artifact identifier;
- selected artifact identifier;
- target path ACLI plans to create;
- target path mode;
- content preview;
- proposed repository changes;
- diagnostics.

This lets the operator verify the intended artifact name before approval.

### 3.6 Replay Evidence

Proposal capture replay now includes:

- `proposal_naming_decision`;
- `proposal_preview_artifact`;
- requested identifier;
- selected identifier;
- selected target path;
- target path mode;
- collision status;
- proposal preview hash.

This preserves replay reconstruction and audit visibility for naming decisions.

## 4. Approval Binding Preservation

Approval still binds to the final governed development proposal artifact hash.

Because naming and target path selection occur before the proposal hash is computed, any change to selected artifact name, target path, or content changes the proposal hash and therefore requires a new approval.

## 5. Fail-Closed Preservation

The implementation fails closed when:

- more than one explicit artifact identifier is detected;
- requested target path already exists;
- generated fallback target path already exists;
- target path would escape the workspace.

Failure occurs before approval, worker invocation, validation, or repository mutation.

## 6. Validation Results

Executed validation:

```text
python -m py_compile aigol/runtime/acli_governed_development_execution_bridge.py
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
python -m pytest tests/test_conversational_cli_runtime_v1.py -q
git diff --check
```

Expected result:

```text
all pass
```

## 7. Final Verdict

Governed development proposals now preserve explicit operator-provided artifact names and governance artifact identifiers when deterministically safe.

Replay determinism, approval binding, deterministic fallback naming, collision fail-closed behavior, and operator-visible proposal previews are preserved.

```text
ACLI_PROPOSAL_CONTENT_FIDELITY_IMPLEMENTED
```
