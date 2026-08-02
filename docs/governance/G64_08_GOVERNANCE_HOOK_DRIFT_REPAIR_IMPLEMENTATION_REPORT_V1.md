# 1. Implementation Summary

Generation: G64-08

Report identity:
G64_08_GOVERNANCE_HOOK_DRIFT_REPAIR_IMPLEMENTATION_REPORT_V1

Reporting date: 2026-08-02

Constitutional baseline:
CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_ESTABLISHED

Authenticated repository anchor:

- Commit: `b778fef0aae1b2d542279dd76f4f32aa1756c7f6`
- Direct parent: `0ab4f34d8e13e19e75220046ccebc44869018e7e`
- Tree: `14a83f71b4b98cc91a10f715218ff25da85d69dd`
- Subject: `G64-07: establish constitutional certification completion gate`
- G64-07 report SHA-256:
  `c7a8ceee750f5b0cd0dc37605e6626899bb3f58fdc9ba09e493bb965b4ad5695`
- Implementation-start worktree state: clean

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G64-07 Constitutional Certification Completion Gate Implementation Report
  V1
- G64-05 Constitutional Governance Revalidation Report V1
- G64-02 Constitutional Governance Closure Repair Sequencing Report V1
- Governance Conformance System V1
- Canonical nested `sapianta_system/scripts/hooks/pre-commit`
- AGENTS.md SAPIANTA Codex Orchestration Guide

Objective:

Eliminate only the authenticated root and nested pre-commit governance-hook
drift retained by G64-05, while preserving all certified runtime ownership and
behavior.

Implemented scope:

- Added the missing canonical root `scripts/hooks/pre-commit` enforcement
  surface.
- Made the root hook run the existing read-only repository conformance owner
  and delegate nested constitutional checks to the canonical nested hook.
- Added a deterministic fail-closed installer that copies exact canonical hook
  bytes to the root and nested Git hook locations and verifies byte equality.
- Installed the root hook at `.git/hooks/pre-commit`.
- Replaced the stale nested installed hook at
  `sapianta_system/.git/hooks/pre-commit` with the exact existing canonical
  nested hook.
- Added focused installation, exact-byte, conformance, and fail-closed tests.

Modified enforcement surfaces:

- `scripts/hooks/pre-commit`: new tracked root enforcement hook.
- `scripts/install_governance_hooks.sh`: new tracked deterministic installer.
- `.git/hooks/pre-commit`: installed root hook, local Git metadata.
- `sapianta_system/.git/hooks/pre-commit`: repaired installed nested hook,
  nested Git metadata.
- `tests/test_g64_08_governance_hook_drift_repair.py`: focused regression
  suite.
- This G48 implementation report.

Intentionally unchanged modules:

- Platform Core and Conversation Layer.
- G47 Development Governance.
- Replay, Authorization, and Worker owners.
- G63 Reuse Proof Runtime and production gate.
- G64-07 constitutional Certification completion gate.
- Governance conformance rules, engine, models, and status semantics.
- The canonical tracked nested hook and all nested governance runtimes.
- Providers, registries, policies, manifests, and prior governance evidence.

Architectural boundaries preserved:

- The root hook invokes the existing conformance owner; it does not duplicate
  conformance evaluation logic.
- Promotion Gate v0.2 and Layer Freeze remain owned and executed by the
  existing canonical nested hook.
- Missing canonical sources, missing installation directories, byte mismatch,
  conformance failure, or nested-hook failure block installation or commit.
- Hook execution grants no approval, Authorization, Worker, Certification, or
  promotion authority.

Implementation determination:

Both expected/installed hook pairs now contain the required
`promotion_gate_v02` and `check_layer_freeze` enforcement coverage. Root and
nested installed bytes exactly match their canonical sources. The unchanged
conformance engine reports `CONFORMANT`, 20 passes, 0 failures, 0 warnings, and
0 critical violations.

# 2. Code Evidence

## Hook evidence inventory

| Evidence | SHA-256 | Determination |
|---|---|---|
| `scripts/hooks/pre-commit` | `6ed569591d4b460f44b81153eedb6401af253bd587f77285c95cfcad92a27b0f` | Canonical root hook |
| `.git/hooks/pre-commit` | `6ed569591d4b460f44b81153eedb6401af253bd587f77285c95cfcad92a27b0f` | Exact installed root hook |
| `sapianta_system/scripts/hooks/pre-commit` | `b4ff04a5f4865585aefc627da23fa7a97fa5b93655c5c7cb28bddcf3a1d91987` | Existing canonical nested hook |
| `sapianta_system/.git/hooks/pre-commit` | `b4ff04a5f4865585aefc627da23fa7a97fa5b93655c5c7cb28bddcf3a1d91987` | Exact repaired nested installation |
| `scripts/install_governance_hooks.sh` | `ebdb81e8bf36d577eea7baa8742f4372abfe4f4b2ac4b21f1465ab317651e8ee` | Deterministic exact-byte installer |
| `test_g64_08_governance_hook_drift_repair.py` | `517cbf6fb81d06f5937c5472fade6d5d5a8fe59775584c6e8115f3af0e5f11cd` | Focused repair and fail-closed proof |

The hashes identify the validated pre-report bytes. This report does not
change those hook, installer, or test bytes.

## Root hook ownership

The root hook performs two bounded orchestration actions:

```text
python3 -m runtime.governance.governance_conformance_engine
-> existing sapianta_system/scripts/hooks/pre-commit
```

The first action reuses the read-only conformance owner. The second action
reuses the canonical nested enforcement sequence, which already owns:

- `tools/governance/promotion_gate_v02.py --staged`;
- structural-change fail-closed handling and explicit override semantics;
- `scripts/check_layer_freeze.py`;
- existing IGL, kernel boundary, dependency, determinism, and repeatability
  checks.

No enforcement algorithm was copied into the root hook.

## Deterministic installation

`scripts/install_governance_hooks.sh` installs only these exact pairs:

```text
scripts/hooks/pre-commit
-> .git/hooks/pre-commit

sapianta_system/scripts/hooks/pre-commit
-> sapianta_system/.git/hooks/pre-commit
```

For each pair the installer:

1. requires the canonical source;
2. requires the exact target directory;
3. copies canonical bytes;
4. applies executable mode `0755`;
5. compares source and installed bytes with `cmp`;
6. fails closed on any missing surface or mismatch.

## Authenticated drift resolution

| G64-05 hook finding | Before G64-08 | G64-08 evidence | State |
|---|---|---|---|
| Root expected hook missing | `scripts/hooks/pre-commit` absent | Tracked canonical hook added with both required tokens | `RESOLVED` |
| Root installed hook missing | `.git/hooks/pre-commit` absent | Installed file is executable and byte-identical to canonical root hook | `RESOLVED` |
| Nested installed hook missing Promotion Gate | Installed hook lacked `promotion_gate_v02` | Installed file exactly matches canonical nested hook | `RESOLVED` |
| Nested installed hook missing Layer Freeze | Installed hook lacked `check_layer_freeze` | Installed file exactly matches canonical nested hook | `RESOLVED` |

## Conformance result

The unchanged conformance owner returned:

```json
{
  "checks_failed": 0,
  "checks_passed": 20,
  "critical_violations": 0,
  "deterministic": true,
  "fail_closed": true,
  "read_only": true,
  "report_hash": "5b87813dac8851b2a30280c40c9c35f27fb922f234ab886a562b3a948bd604cd",
  "status": "CONFORMANT",
  "violations": [],
  "warnings": 0
}
```

# 3. Constitutional Self-Assessment

## Verified

- Root canonical and installed hook bytes are identical.
- Nested canonical and installed hook bytes are identical.
- All four hook files are executable.
- Both expected/installed pairs expose the conformance-required
  `promotion_gate_v02` and `check_layer_freeze` coverage.
- Missing installation targets fail closed.
- Root conformance failure stops hook execution before nested enforcement.
- The deterministic installer reproduces a conformant 20/20 fixture.
- The actual repository conformance owner reports `CONFORMANT` with no
  violations or warnings.
- The broader G64 completion, constitutional Certification, promotion, and
  conformance regression set passes.
- No certified Python runtime or constitutional ownership contract changed.

## Not Verified

- G64-08 does not repair the separately authenticated direct-provider
  selection ownership exceptions.
- G64-08 does not implement the later repository-wide cross-entry negative
  closure suite.
- Git hook installation is repository-local metadata; a fresh clone must run
  `scripts/install_governance_hooks.sh` to reproduce the exact installed
  surfaces.
- G64-08 does not grant or execute a Git commit, promotion, deployment, or
  external-provider action.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Authenticate G64-07 baseline | Commit, parent, tree, subject, report hash | Git identity and clean start-state review | `PASS` |
| Root hook conformance | Canonical and installed root hook | SHA-256 and `cmp -s` | `PASS` |
| Nested hook conformance | Canonical and installed nested hook | SHA-256 and `cmp -s` | `PASS` |
| Required enforcement coverage | Root delegation and canonical nested commands | Static inspection plus conformance owner | `PASS` |
| Deterministic installation | Exact-byte installer | Focused temporary-repository test | `PASS` |
| Installer fail-closed behavior | Missing target directory | Focused negative test | `PASS` |
| Hook fail-closed behavior | Simulated `PARTIALLY_CONFORMANT` owner result | Root hook exits before nested hook | `PASS` |
| Governance conformance tests | Existing five conformance tests plus three G64-08 tests | 8 passed | `PASS` |
| Actual governance conformance | Unchanged conformance engine | 20 passed, 0 failed, `CONFORMANT` | `PASS` |
| Regression compatibility | G64-04, G64-06, G64-07, Certification, promotion, and conformance modules | 62 passed | `PASS` |
| Fail-closed runtime compatibility | Existing G64-04/G64-07 negative suites | Included in 62 passing tests | `PASS` |
| Python compilation | Focused test, conformance modules, and preserved G64-07 completion gate | `python -m py_compile ...` | `PASS` |
| Shell syntax | Root hook, installer, and canonical nested hook | `sh -n ...` | `PASS` |
| Diff whitespace integrity | Complete tracked implementation diff | `git diff --check` | `PASS` |
| Runtime provider behavior | No provider call authorized | Not required for hook conformance | `NOT_APPLICABLE` |

# 5. Repository Mutation Summary

Tracked outer-repository additions:

- `scripts/hooks/pre-commit`
- `scripts/install_governance_hooks.sh`
- `tests/test_g64_08_governance_hook_drift_repair.py`
- `docs/governance/G64_08_GOVERNANCE_HOOK_DRIFT_REPAIR_IMPLEMENTATION_REPORT_V1.md`

Installed local enforcement metadata:

- `.git/hooks/pre-commit`
- `sapianta_system/.git/hooks/pre-commit`

Unchanged tracked nested-repository source:

- `sapianta_system/scripts/hooks/pre-commit`

Unchanged certified subsystems:

- Platform Core, Conversation Layer, and Development Governance.
- Replay, Authorization, Worker, and mutation owners.
- G63 Reuse Proof and production admission.
- G64-07 constitutional Certification completion gate.
- Governance conformance engine, rules, models, and constitutional evidence.
- Providers, registries, policies, manifests, and release mechanisms.

API compatibility:

- No Python API, artifact schema, route, state transition, Authorization,
  Worker, Replay, Certification, provider, registry, or persistence contract
  changed.
- Hook installation is additive and deterministic.
- The nested expected hook is reused without modification.

Rollback strategy:

- If canonical hook execution cannot be trusted, commits remain blocked.
- Reinstall from tracked canonical sources; do not weaken, skip, or replace
  required governance checks.
- Installed hooks are reproducible local metadata. Removing the tracked
  installer or expected hook is not an authorized compatibility fallback.

Unrelated pre-existing changes:

- None observed at implementation start.

# 6. Certification Verdict

GOVERNANCE_HOOK_DRIFT_REPAIRED
