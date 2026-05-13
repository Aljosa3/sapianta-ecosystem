"""Root pytest collection topology for SAPIANTA.

Generated runtime artifacts are not source tests for root collection. They are
preserved on disk but ignored during collection so stale generated modules and
duplicate generated names cannot destabilize governance validation.
"""

from __future__ import annotations

from pathlib import Path


_IGNORED_COLLECTION_ROOTS = {
    Path("runtime/development/generated"),
    Path("runtime/development/quarantine"),
    Path("sapianta_system/runtime/development/generated"),
    Path("sapianta_system/runtime/development/quarantine"),
    Path("sapianta_system/sapianta_product/generated"),
}


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # noqa: ANN001
    try:
        relative = collection_path.relative_to(config.rootpath)
    except ValueError:
        return False
    return any(relative == root or root in relative.parents for root in _IGNORED_COLLECTION_ROOTS)
