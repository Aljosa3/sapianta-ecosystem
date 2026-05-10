"""Read-only governance conformance verification for SAPIANTA.

This module verifies alignment between constitutional documentation, runtime
guards, mutation governance, replay guarantees, and installed hook evidence.
It does not mutate runtime behavior or repair governance drift.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .conformance_models import (
    ConformanceReport,
    ConformanceStatus,
    ConformanceViolation,
    EnforcementStatus,
    InvariantCheckResult,
    Severity,
)
from .conformance_rules import (
    CONSTITUTIONAL_DOCS,
    ENFORCEMENT_CONTENT_RULES,
    HOOK_REQUIRED_TOKENS,
    LINEAGE_EVIDENCE,
    evaluate_content_rule,
    evaluate_existence_rule,
    read_text,
)


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


class GovernanceConformanceEngine:
    """Deterministic, read-only constitutional conformance engine."""

    def __init__(self, repository_root: str | Path = ".") -> None:
        self.repository_root = Path(repository_root).resolve()

    def run(self) -> ConformanceReport:
        checks: list[InvariantCheckResult] = []
        checks.extend(self._check_constitutional_docs())
        checks.extend(self._check_enforcement_integrity())
        checks.extend(self._check_hook_integrity())
        checks.extend(self._check_lineage_integrity())

        violations = tuple(
            violation
            for violation in (check.to_violation() for check in checks)
            if violation is not None
        )
        checks_passed = sum(1 for check in checks if check.status is EnforcementStatus.PASS)
        checks_failed = len(checks) - checks_passed
        critical_violations = sum(
            1 for violation in violations if violation.severity is Severity.CRITICAL
        )
        warnings = sum(1 for violation in violations if violation.severity is Severity.WARNING)
        status = self._classify_status(violations, checks_failed)

        report_without_hash = ConformanceReport(
            status=status,
            critical_violations=critical_violations,
            warnings=warnings,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            violations=violations,
            checks=tuple(checks),
        )
        report_hash = stable_hash(report_without_hash.to_dict(include_hash=False))
        return ConformanceReport(
            status=status,
            critical_violations=critical_violations,
            warnings=warnings,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            violations=violations,
            checks=tuple(checks),
            report_hash=report_hash,
        )

    def _check_constitutional_docs(self) -> list[InvariantCheckResult]:
        return [evaluate_existence_rule(self.repository_root, rule) for rule in CONSTITUTIONAL_DOCS]

    def _check_enforcement_integrity(self) -> list[InvariantCheckResult]:
        return [
            evaluate_content_rule(self.repository_root, rule)
            for rule in ENFORCEMENT_CONTENT_RULES
        ]

    def _check_lineage_integrity(self) -> list[InvariantCheckResult]:
        return [evaluate_existence_rule(self.repository_root, rule) for rule in LINEAGE_EVIDENCE]

    def _check_hook_integrity(self) -> list[InvariantCheckResult]:
        checks = [
            self._check_hook_pair(
                "HOOK-ROOT-PRECOMMIT",
                "root pre-commit governance enforcement",
                "scripts/hooks/pre-commit",
                ".git/hooks/pre-commit",
                Severity.WARNING,
            ),
            self._check_hook_pair(
                "HOOK-SYSTEM-PRECOMMIT",
                "sapianta_system pre-commit governance enforcement",
                "sapianta_system/scripts/hooks/pre-commit",
                "sapianta_system/.git/hooks/pre-commit",
                Severity.HIGH,
            ),
        ]
        return checks

    def _check_hook_pair(
        self,
        check_id: str,
        surface: str,
        expected_path: str,
        installed_path: str,
        severity: Severity,
    ) -> InvariantCheckResult:
        expected = read_text(self.repository_root, expected_path)
        installed = read_text(self.repository_root, installed_path)
        if expected is None and installed is None:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=installed_path,
                expected=f"{expected_path} and installed hook with governance tokens",
                actual="expected and installed hooks missing",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        if expected is None:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=expected_path,
                expected="expected governance hook script",
                actual="missing",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        if installed is None:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=installed_path,
                expected="installed hook with governance tokens",
                actual="missing",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )

        missing_expected = tuple(token for token in HOOK_REQUIRED_TOKENS if token not in expected)
        missing_installed = tuple(token for token in HOOK_REQUIRED_TOKENS if token not in installed)
        if missing_expected:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=expected_path,
                expected="expected hook declares governance enforcement tokens",
                actual="missing tokens: " + ", ".join(missing_expected),
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        if missing_installed:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=installed_path,
                expected=", ".join(HOOK_REQUIRED_TOKENS),
                actual="missing tokens: " + ", ".join(missing_installed),
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        return InvariantCheckResult(
            check_id=check_id,
            status=EnforcementStatus.PASS,
            surface=installed_path,
            expected="installed hook contains governance enforcement tokens",
            actual="present",
            severity=severity,
            violation_type="HOOK_MISMATCH",
        )

    @staticmethod
    def _classify_status(
        violations: tuple[ConformanceViolation, ...], checks_failed: int
    ) -> ConformanceStatus:
        if any(violation.severity is Severity.CRITICAL for violation in violations):
            return ConformanceStatus.CRITICAL_VIOLATION
        if not violations:
            return ConformanceStatus.CONFORMANT
        if any(violation.severity is Severity.HIGH for violation in violations):
            return ConformanceStatus.PARTIALLY_CONFORMANT
        if checks_failed > 0:
            return ConformanceStatus.PARTIALLY_CONFORMANT
        return ConformanceStatus.CONFORMANT


def run_conformance_check(repository_root: str | Path = ".") -> dict[str, object]:
    return GovernanceConformanceEngine(repository_root).run().to_dict()


if __name__ == "__main__":
    print(json.dumps(run_conformance_check(), sort_keys=True, indent=2))

