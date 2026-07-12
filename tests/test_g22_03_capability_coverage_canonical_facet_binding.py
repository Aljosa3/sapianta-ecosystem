"""G22-03 regressions for canonical Capability Coverage facet binding."""

from __future__ import annotations

from aigol.runtime.platform_capability_composition_coverage import (
    COVERAGE_FAILED_CLOSED,
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_development_composition_plan import (
    DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED,
    compose_platform_development_plan,
)


CREATED_AT = "2026-07-12T00:00:00Z"
OPERATIONAL_READINESS_REQUEST = """# G22-02 — Copy/Paste Independence Operational Readiness Certification Audit

Perform an AUDIT_ONLY operational readiness certification.

Determine whether Platform Core is operationally capable of supporting the complete governed development workflow through ./aicli without manual copy/paste between development phases.

Evaluate the complete lifecycle:

Human Request
↓
Semantic Interpretation
↓
Project Objective
↓
Capability Discovery
↓
Capability Coverage
↓
Development Composition Plan
↓
Durable Governed Work Artifact
↓
Human Approval
↓
Authorized Worker Execution
↓
Replay
↓
Certification

Do not implement anything. Do not modify code, tests, runtime, or ./aicli.
"""


def test_operational_request_binds_canonical_capability_coverage_facet() -> None:
    coverage = discover_platform_capability_composition_coverage(
        query=OPERATIONAL_READINESS_REQUEST,
        created_at=CREATED_AT,
    )

    assert coverage["request_facet_count"] > 0
    assert any(
        facet["facet"] == "CAPABILITY_COMPOSITION_DISCOVERY"
        and "capability coverage" in facet["matched_terms"]
        for facet in coverage["request_facets"]
    )
    assert coverage["coverage_status"] != COVERAGE_FAILED_CLOSED
    assert coverage["provider_invoked"] is False
    assert coverage["worker_invoked"] is False
    assert coverage["repository_mutated"] is False

    plan = compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=CREATED_AT,
    )

    assert plan["plan_status"] != DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED
    assert plan["provider_invoked"] is False
    assert plan["worker_invoked"] is False
    assert plan["repository_mutated"] is False


def test_genuinely_unknown_capability_request_still_fails_closed() -> None:
    coverage = discover_platform_capability_composition_coverage(
        query="Evaluate flibbertigibbet topology.",
        created_at=CREATED_AT,
    )

    assert coverage["request_facets"] == []
    assert coverage["coverage_status"] == COVERAGE_FAILED_CLOSED
    assert coverage["provider_invoked"] is False
    assert coverage["worker_invoked"] is False
    assert coverage["repository_mutated"] is False
