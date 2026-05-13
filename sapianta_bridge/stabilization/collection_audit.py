"""Deterministic collection blocker classification."""

from __future__ import annotations

import re

from .collection_models import CollectionBlocker, audit_report


OPTIONAL_MODULES = {
    "numpy",
    "hypothesis",
    "credit_domain",
    "sapianta_domain_trading",
    "sapianta_core",
}


def classify_blocker(path: str, error_type: str, message: str) -> CollectionBlocker:
    text = f"{path} {error_type} {message}".lower()
    if "__pycache__" in text or "/generated/" in text or "/quarantine/" in text:
        return CollectionBlocker(
            path=path,
            error_type=error_type,
            classification="STALE_GENERATED_ARTIFACT",
            recommended_action="exclude generated/cache runtime artifacts from root collection",
        )
    if any(module in text for module in OPTIONAL_MODULES):
        return CollectionBlocker(
            path=path,
            error_type=error_type,
            classification="OPTIONAL_DEPENDENCY",
            recommended_action="document optional dependency or add source-specific import guard",
        )
    if "venv/" in text or "site-packages" in text or "sapianta_system/" in text:
        return CollectionBlocker(
            path=path,
            error_type=error_type,
            classification="NESTED_PROJECT_SURFACE",
            recommended_action="isolate nested project or virtualenv surface from root collection",
        )
    if "modulenotfounderror" in text or "importerror" in text or "attempted relative import" in text:
        return CollectionBlocker(
            path=path,
            error_type=error_type,
            classification="IMPORT_TOPOLOGY",
            recommended_action="stabilize package import topology without changing runtime behavior",
        )
    if "assertionerror" in text:
        return CollectionBlocker(
            path=path,
            error_type=error_type,
            classification="REAL_TEST_FAILURE",
            recommended_action="report separately from collection stabilization",
        )
    return CollectionBlocker(
        path=path,
        error_type=error_type,
        classification="UNKNOWN",
        recommended_action="manual governance review required",
    )


def blockers_from_pytest_output(output: str) -> list[CollectionBlocker]:
    blockers: list[CollectionBlocker] = []
    current_path = "unknown"
    for line in output.splitlines():
        if line.startswith("_ ERROR collecting "):
            current_path = line.strip("_ ").replace("ERROR collecting ", "").strip()
        match = re.search(r"(ModuleNotFoundError|ImportError|NameError|AssertionError): (.+)", line)
        if match:
            blockers.append(classify_blocker(current_path, match.group(1), match.group(2)))
    return blockers


def build_collection_audit(collection_passed: bool, output: str) -> dict:
    blockers = [] if collection_passed else blockers_from_pytest_output(output)
    return audit_report("PASSED" if collection_passed else "FAILED", blockers)
