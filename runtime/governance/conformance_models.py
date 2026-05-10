"""Deterministic models for SAPIANTA governance conformance checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConformanceStatus(str, Enum):
    CONFORMANT = "CONFORMANT"
    PARTIALLY_CONFORMANT = "PARTIALLY_CONFORMANT"
    NON_CONFORMANT = "NON_CONFORMANT"
    CRITICAL_VIOLATION = "CRITICAL_VIOLATION"


class EnforcementStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class GovernanceSurface:
    surface_id: str
    path: str
    layer: str
    expected_status: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "expected_status": self.expected_status,
            "layer": self.layer,
            "path": self.path,
            "surface_id": self.surface_id,
        }


@dataclass(frozen=True)
class ConformanceViolation:
    violation_type: str
    severity: Severity
    surface: str
    expected: str
    actual: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "actual": self.actual,
            "evidence": self.evidence,
            "expected": self.expected,
            "severity": self.severity.value,
            "surface": self.surface,
            "type": self.violation_type,
        }


@dataclass(frozen=True)
class InvariantCheckResult:
    check_id: str
    status: EnforcementStatus
    surface: str
    expected: str
    actual: str
    severity: Severity = Severity.WARNING
    violation_type: str = "CONFORMANCE_FAILURE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "actual": self.actual,
            "check_id": self.check_id,
            "expected": self.expected,
            "severity": self.severity.value,
            "status": self.status.value,
            "surface": self.surface,
            "violation_type": self.violation_type,
        }

    def to_violation(self) -> ConformanceViolation | None:
        if self.status is EnforcementStatus.PASS:
            return None
        return ConformanceViolation(
            violation_type=self.violation_type,
            severity=self.severity,
            surface=self.surface,
            expected=self.expected,
            actual=self.actual,
            evidence=self.check_id,
        )


@dataclass(frozen=True)
class ConformanceReport:
    status: ConformanceStatus
    critical_violations: int
    warnings: int
    checks_passed: int
    checks_failed: int
    violations: tuple[ConformanceViolation, ...] = field(default_factory=tuple)
    checks: tuple[InvariantCheckResult, ...] = field(default_factory=tuple)
    report_hash: str = ""
    deterministic: bool = True
    read_only: bool = True
    fail_closed: bool = True

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "checks_failed": self.checks_failed,
            "checks_passed": self.checks_passed,
            "critical_violations": self.critical_violations,
            "deterministic": self.deterministic,
            "fail_closed": self.fail_closed,
            "read_only": self.read_only,
            "status": self.status.value,
            "violations": [violation.to_dict() for violation in self.violations],
            "warnings": self.warnings,
        }
        if include_hash:
            data["report_hash"] = self.report_hash
        return data

