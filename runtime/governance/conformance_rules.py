"""Canonical rule definitions for governance conformance verification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .conformance_models import EnforcementStatus, InvariantCheckResult, Severity


@dataclass(frozen=True)
class ContentRule:
    check_id: str
    surface: str
    path: str
    expected: str
    required_tokens: tuple[str, ...]
    severity: Severity
    violation_type: str


@dataclass(frozen=True)
class ExistenceRule:
    check_id: str
    surface: str
    path: str
    expected: str
    severity: Severity
    violation_type: str


CONSTITUTIONAL_DOCS: tuple[ExistenceRule, ...] = (
    ExistenceRule(
        "DOC-CONSTITUTIONAL-SPEC",
        "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
        "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
        "constitutional specification exists",
        Severity.CRITICAL,
        "MISSING_CONSTITUTIONAL_SPEC",
    ),
    ExistenceRule(
        "DOC-LAYER-MODEL",
        "docs/governance/CANONICAL_LAYER_MODEL.md",
        "docs/governance/CANONICAL_LAYER_MODEL.md",
        "canonical layer model exists",
        Severity.CRITICAL,
        "MISSING_CONSTITUTIONAL_SPEC",
    ),
    ExistenceRule(
        "DOC-INVARIANTS",
        "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
        "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
        "constitutional invariants exist",
        Severity.CRITICAL,
        "MISSING_CONSTITUTIONAL_SPEC",
    ),
    ExistenceRule(
        "DOC-ENFORCEMENT-HIERARCHY",
        "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
        "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
        "governance enforcement hierarchy exists",
        Severity.CRITICAL,
        "MISSING_CONSTITUTIONAL_SPEC",
    ),
    ExistenceRule(
        "DOC-LINEAGE",
        "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "governance lineage model exists",
        Severity.HIGH,
        "MISSING_LINEAGE_EVIDENCE",
    ),
)


ENFORCEMENT_CONTENT_RULES: tuple[ContentRule, ...] = (
    ContentRule(
        "L0-FREEZE-MANIFEST",
        "sapianta_system/governance/phases/LAYER_0_FREEZE.yaml",
        "sapianta_system/governance/phases/LAYER_0_FREEZE.yaml",
        "Layer 0 freeze manifest declares locked files",
        ("layer: 0", "locked_files", "core_constitutional"),
        Severity.CRITICAL,
        "MISSING_FREEZE_ENFORCEMENT",
    ),
    ContentRule(
        "L0-FREEZE-CHECKER",
        "sapianta_system/scripts/check_layer_freeze.py",
        "sapianta_system/scripts/check_layer_freeze.py",
        "Layer 0 freeze checker rejects changed locked files",
        ("LAYER_0_FREEZE.yaml", "locked_files", "SAPIANTA_FREEZE_OVERRIDE"),
        Severity.CRITICAL,
        "MISSING_FREEZE_ENFORCEMENT",
    ),
    ContentRule(
        "ARCHITECTURE-GUARDIAN-PROTECTION",
        "sapianta_system/runtime/development/architecture_guardian.py",
        "sapianta_system/runtime/development/architecture_guardian.py",
        "ArchitectureGuardian protects governance/replay/kernel/constitution paths",
        ("protected_paths", "runtime/governance", "runtime/layer2", "eval", "exec"),
        Severity.CRITICAL,
        "MISSING_PROTECTED_PATH_ENFORCEMENT",
    ),
    ContentRule(
        "MUTATION-GUARD-PROTECTION",
        "sapianta_system/runtime/development/mutation_guard.py",
        "sapianta_system/runtime/development/mutation_guard.py",
        "MutationGuard rejects protected runtime paths",
        ("FORBIDDEN_PATHS", "runtime/governance", "runtime/ledger", "runtime/layer2"),
        Severity.HIGH,
        "MISSING_MUTATION_BOUNDARY",
    ),
    ContentRule(
        "MUTATION-VALIDATOR-LAYERS",
        "sapianta_system/runtime/development/mutation_validator.py",
        "sapianta_system/runtime/development/mutation_validator.py",
        "MutationValidator classifies L0/L1 as immutable",
        ('"L0": "IMMUTABLE"', '"L1": "IMMUTABLE"', "check_mutation_permission"),
        Severity.HIGH,
        "INVALID_LAYER_MAPPING",
    ),
    ContentRule(
        "PROMOTION-GATE",
        "sapianta_system/runtime/governance/promotion_gate.py",
        "sapianta_system/runtime/governance/promotion_gate.py",
        "Promotion gate classifies structural and parametric changes",
        ("STRUCTURAL", "PARAMETRIC", "requires_approval"),
        Severity.HIGH,
        "MISSING_PROMOTION_GATE",
    ),
    ContentRule(
        "DEV-GOVERNANCE-GATE",
        "sapianta_system/runtime/development/dev_governance_gate.py",
        "sapianta_system/runtime/development/dev_governance_gate.py",
        "Development governance gate blocks dangerous tasks",
        ("BLOCK", "REVIEW", "Fail-closed", "approved_by_human"),
        Severity.HIGH,
        "MISSING_GOVERNANCE_GATE",
    ),
    ContentRule(
        "CCS-CERTIFICATION",
        "sapianta_system/runtime/development/ccs/certification_engine.py",
        "sapianta_system/runtime/development/ccs/certification_engine.py",
        "CCS certification requires Guardian validation and strict tests",
        ("ArchitectureGuardian", "run_strict_generated_tests", "CERTIFIED", "REJECTED"),
        Severity.HIGH,
        "MISSING_CERTIFICATION_GATE",
    ),
    ContentRule(
        "REPLAY-CHAIN-VERIFIER",
        "sapianta_system/runtime/governance/chain_verifier.py",
        "sapianta_system/runtime/governance/chain_verifier.py",
        "Replay chain verifier recomputes hash linkage",
        ("previous_hash", "stable_hash", "verify"),
        Severity.HIGH,
        "MISSING_REPLAY_GUARANTEE",
    ),
    ContentRule(
        "REPLAY-ENGINE",
        "sapianta_system/runtime/governance/replay_engine.py",
        "sapianta_system/runtime/governance/replay_engine.py",
        "Replay engine verifies deterministic envelope equivalence",
        ("ReplayMismatchError", "replay", "hash"),
        Severity.HIGH,
        "MISSING_REPLAY_GUARANTEE",
    ),
)


LINEAGE_EVIDENCE: tuple[ExistenceRule, ...] = (
    ExistenceRule(
        "AUDIT-LAYER-MAP",
        "docs/governance_audit/GOVERNANCE_LAYER_MAP.md",
        "docs/governance_audit/GOVERNANCE_LAYER_MAP.md",
        "governance layer audit evidence exists",
        Severity.HIGH,
        "MISSING_GOVERNANCE_LINEAGE",
    ),
    ExistenceRule(
        "AUDIT-LAYER0",
        "docs/governance_audit/LAYER0_CONSTITUTION_ANALYSIS.md",
        "docs/governance_audit/LAYER0_CONSTITUTION_ANALYSIS.md",
        "Layer 0 audit evidence exists",
        Severity.HIGH,
        "MISSING_GOVERNANCE_LINEAGE",
    ),
    ExistenceRule(
        "AUDIT-GAPS",
        "docs/governance_audit/GOVERNANCE_GAP_ANALYSIS.md",
        "docs/governance_audit/GOVERNANCE_GAP_ANALYSIS.md",
        "governance gap evidence exists",
        Severity.WARNING,
        "MISSING_GOVERNANCE_LINEAGE",
    ),
)


HOOK_REQUIRED_TOKENS = ("promotion_gate_v02", "check_layer_freeze")


def read_text(root: Path, relative_path: str) -> str | None:
    path = root / relative_path
    if not path.exists() or not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def evaluate_existence_rule(root: Path, rule: ExistenceRule) -> InvariantCheckResult:
    path = root / rule.path
    exists = path.exists() and path.is_file()
    return InvariantCheckResult(
        check_id=rule.check_id,
        status=EnforcementStatus.PASS if exists else EnforcementStatus.FAIL,
        surface=rule.surface,
        expected=rule.expected,
        actual="present" if exists else "missing",
        severity=rule.severity,
        violation_type=rule.violation_type,
    )


def evaluate_content_rule(root: Path, rule: ContentRule) -> InvariantCheckResult:
    text = read_text(root, rule.path)
    if text is None:
        return InvariantCheckResult(
            check_id=rule.check_id,
            status=EnforcementStatus.FAIL,
            surface=rule.surface,
            expected=rule.expected,
            actual="missing",
            severity=rule.severity,
            violation_type=rule.violation_type,
        )
    missing = tuple(token for token in rule.required_tokens if token not in text)
    return InvariantCheckResult(
        check_id=rule.check_id,
        status=EnforcementStatus.PASS if not missing else EnforcementStatus.FAIL,
        surface=rule.surface,
        expected=rule.expected,
        actual="present" if not missing else "missing tokens: " + ", ".join(missing),
        severity=rule.severity,
        violation_type=rule.violation_type,
    )
