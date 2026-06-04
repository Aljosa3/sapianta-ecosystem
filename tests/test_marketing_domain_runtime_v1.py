"""Tests for the deterministic placeholder Marketing domain runtime."""

from aigol.runtime.marketing_domain_runtime import (
    MARKETING_DOMAIN_RUNTIME_VERSION,
    describe_marketing_domain,
)


def test_marketing_domain_runtime_identity() -> None:
    assert describe_marketing_domain() == {
        "domain": "MARKETING",
        "runtime_version": MARKETING_DOMAIN_RUNTIME_VERSION,
        "implementation_status": "PLACEHOLDER",
    }
