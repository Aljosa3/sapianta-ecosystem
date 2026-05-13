"""Explicit optional dependency policy for collection stabilization."""

from __future__ import annotations


OPTIONAL_DEPENDENCY_RULES = {
    "numpy": "optional runtime/domain analytics dependency; absence must not crash unrelated governance collection",
    "hypothesis": "optional third-party test dependency surfaced by nested virtualenv collection",
    "credit_domain": "optional domain package surfaced only when credit domain tests are collected",
    "sapianta_domain_trading": "optional nested domain package surfaced only when trading domain tests are collected",
    "sapianta_core_proposal_api": "legacy optional credit flow API; guarded at module level",
}


def optional_dependency_action(module_name: str) -> dict[str, str | bool]:
    known = module_name in OPTIONAL_DEPENDENCY_RULES
    return {
        "module": module_name,
        "known_optional": known,
        "allowed_handling": "source-specific import guard or explicit package path"
        if known
        else "manual review required",
        "broad_skip_allowed": False,
        "reason": OPTIONAL_DEPENDENCY_RULES.get(module_name, "dependency is not classified optional"),
    }


def optional_dependency_manifest() -> dict:
    return {
        "optional_dependencies": dict(sorted(OPTIONAL_DEPENDENCY_RULES.items())),
        "core_governance_tests_optional": False,
        "broad_skip_strategy_allowed": False,
    }
