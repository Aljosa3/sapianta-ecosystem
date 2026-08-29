"""Read-only governance conformance verification for SAPIANTA.

This module verifies alignment between constitutional documentation, runtime
guards, mutation governance, replay guarantees, and installed hook evidence.
It does not mutate runtime behavior or repair governance drift.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
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
                ".",
                Severity.WARNING,
            ),
            self._check_hook_pair(
                "HOOK-SYSTEM-PRECOMMIT",
                "sapianta_system pre-commit governance enforcement",
                "sapianta_system/scripts/hooks/pre-commit",
                "sapianta_system",
                Severity.HIGH,
            ),
        ]
        return checks

    def _resolve_hook_path(self, repository_path: str) -> Path | None:
        repository = self.repository_root / repository_path
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-path",
                    "hooks/pre-commit",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            return None
        lines = result.stdout.splitlines()
        if result.returncode != 0 or len(lines) != 1 or not lines[0]:
            return None
        hook_path = Path(lines[0])
        return hook_path if hook_path.is_absolute() else None

    @staticmethod
    def _read_hook(path: Path) -> tuple[bytes, str] | None:
        if not path.exists() or not path.is_file():
            return None
        try:
            content = path.read_bytes()
            return content, content.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    @staticmethod
    def _hook_surface(repository_path: str) -> str:
        prefix = "root" if repository_path == "." else repository_path
        return f"git-resolved:{prefix}:hooks/pre-commit"

    def _check_hook_pair(
        self,
        check_id: str,
        surface: str,
        expected_path: str,
        repository_path: str,
        severity: Severity,
    ) -> InvariantCheckResult:
        installed_path = self._resolve_hook_path(repository_path)
        installed_surface = self._hook_surface(repository_path)
        if installed_path is None:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=installed_surface,
                expected="active hook path resolved through Git metadata",
                actual="Git hook-path resolution failed",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )

        expected_hook = self._read_hook(self.repository_root / expected_path)
        installed_hook = self._read_hook(installed_path)
        if expected_hook is None:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=expected_path,
                expected="expected governance hook script",
                actual="missing or unreadable",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        if installed_hook is None:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=installed_surface,
                expected="active installed hook with canonical bytes and governance tokens",
                actual="missing or unreadable",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )

        expected_bytes, expected = expected_hook
        installed_bytes, installed = installed_hook
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
                surface=installed_surface,
                expected=", ".join(HOOK_REQUIRED_TOKENS),
                actual="missing tokens: " + ", ".join(missing_installed),
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        if installed_bytes != expected_bytes:
            return InvariantCheckResult(
                check_id=check_id,
                status=EnforcementStatus.FAIL,
                surface=installed_surface,
                expected="active installed hook matches canonical bytes",
                actual="bytes differ from canonical hook",
                severity=severity,
                violation_type="HOOK_MISMATCH",
            )
        return InvariantCheckResult(
            check_id=check_id,
            status=EnforcementStatus.PASS,
            surface=installed_surface,
            expected="active installed hook matches canonical bytes and governance tokens",
            actual="present and byte-identical",
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
