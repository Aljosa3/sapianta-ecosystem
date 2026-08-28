#!/usr/bin/env python3
"""Repository-only regression for one future static EE path binding form."""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any, Callable


sys.dont_write_bytecode = True

GENERATION_IDENTITY = (
    "G77_256EZ_CROSS_ACCOUNT_REPOSITORY_ONLY_STATIC_EE_RUNTIME_PATH_BINDING_"
    "HARDENING_V1"
)
SYNTHETIC_CANDIDATE_IDENTITY = (
    "G77_256EZ_NON_OPERATIONAL_SYNTHETIC_FUTURE_CANDIDATE_BINDING_FIXTURE_V1"
)
REQUIRED_HEAD = "dd54760d41999bc13541b251b3716fa896444d67"
REQUIRED_TREE = "144c39e25956371927644ce03c4a18b60bf8c835"
GUEST_RUNTIME_ROOT = "/mnt/g77-evidence"
RUNTIME_FILENAME = "G77_256EZ_SYNTHETIC_FUTURE_CONTINUATION_MANIFEST_V1.json"
ROOT = ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1"
BINDING_RELATIVE_PATH = (
    f"{ROOT}/binding/G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_FIXTURE_V1.py"
)
DU_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_SHA256 = "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d"
EB_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EB_SHA256 = "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43"
EE_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
)
EE_SHA256 = "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410"
REQUIRED_DECLARATIONS = ("RAW_ROOT", "CONTINUATION_MANIFEST_PATH")


class RegressionError(ValueError):
    """One deterministic EZ regression rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(repository_root: Path, argument: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", argument], cwd=repository_root, text=True
    ).strip()


def _load(repository_root: Path, relative: str, expected_sha256: str, name: str) -> ModuleType:
    path = repository_root / relative
    if sha256_path(path) != expected_sha256:
        raise RegressionError(f"{name.upper()}_HASH_MISMATCH", f"{name} bytes differ")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RegressionError(f"{name.upper()}_IMPORT_FAILED", f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_unambiguous_static_declarations(
    harness_path: Path, ee: ModuleType
) -> tuple[PurePosixPath, PurePosixPath]:
    """Require one declaration per EE name, then delegate grammar parsing to EE."""
    try:
        tree = ast.parse(harness_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise RegressionError("HARNESS_PARSE_FAILED", "harness is not parseable") from exc
    counts = {name: 0 for name in REQUIRED_DECLARATIONS}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name) and target.id in counts:
                counts[target.id] += 1
    if any(count > 1 for count in counts.values()):
        raise RegressionError(
            "DUPLICATE_OR_AMBIGUOUS_STATIC_DECLARATION",
            "each EE path name must have exactly one module-level assignment",
        )
    try:
        return ee.extract_harness_paths(harness_path)
    except Exception as exc:
        code = getattr(exc, "code", type(exc).__name__)
        raise RegressionError(code, "committed EE static extraction rejected") from exc


def _case(case_id: str, expected: str, operation: Callable[[], None]) -> dict[str, str]:
    try:
        operation()
    except Exception as exc:
        observed = getattr(exc, "code", type(exc).__name__)
        return {
            "case_id": case_id,
            "expected_rejection": expected,
            "observed_rejection": observed,
            "result": "PASS" if observed == expected else "FAIL",
        }
    return {
        "case_id": case_id,
        "expected_rejection": expected,
        "observed_rejection": "NOT_REJECTED",
        "result": "FAIL",
    }


def _write_harness(path: Path, body: str) -> Path:
    path.write_text("from pathlib import Path\n\n" + body, encoding="utf-8")
    return path


def _rehash_manifest(envelope: dict[str, Any], du: ModuleType) -> None:
    envelope["manifest_sha256"] = du.sha256_bytes(
        du.canonical_bytes(envelope["manifest"])
    )


def run(repository_root: Path) -> dict[str, Any]:
    if _git(repository_root, "HEAD") != REQUIRED_HEAD:
        raise RegressionError("REQUIRED_HEAD_MISMATCH", "EZ baseline HEAD differs")
    if _git(repository_root, "HEAD^{tree}") != REQUIRED_TREE:
        raise RegressionError("REQUIRED_TREE_MISMATCH", "EZ baseline tree differs")
    du = _load(repository_root, DU_RELATIVE_PATH, DU_SHA256, "du")
    eb = _load(repository_root, EB_RELATIVE_PATH, EB_SHA256, "eb")
    ee = _load(repository_root, EE_RELATIVE_PATH, EE_SHA256, "ee")
    binding = repository_root / BINDING_RELATIVE_PATH
    runtime_root, runtime_path = require_unambiguous_static_declarations(binding, ee)
    if runtime_root != PurePosixPath(GUEST_RUNTIME_ROOT):
        raise RegressionError("STATIC_RAW_ROOT_MISMATCH", "fixture root differs")
    if runtime_path != runtime_root / RUNTIME_FILENAME:
        raise RegressionError(
            "STATIC_CONTINUATION_MANIFEST_PATH_MISMATCH", "fixture path differs"
        )

    cases: list[dict[str, str]] = []
    positive_verification: dict[str, str]
    temporary_path: Path
    with tempfile.TemporaryDirectory(prefix=".g77_256ez_regression_", dir=repository_root) as raw:
        temporary_path = Path(raw)

        def prepare(identity: str) -> tuple[Path, Path, Path]:
            case_root = temporary_path / identity.lower()
            case_root.mkdir()
            candidate = case_root / "candidate.json"
            envelope = du.build_du_fixture(repository_root)
            envelope["manifest"]["generation_identity"] = SYNTHETIC_CANDIDATE_IDENTITY
            envelope["manifest"]["observations"].append(
                "NON_OPERATIONAL_SYNTHETIC_EZ_STATIC_BINDING_REGRESSION_ONLY"
            )
            _rehash_manifest(envelope, du)
            candidate.write_bytes(du.canonical_bytes(envelope))
            eb_receipt = case_root / "eb-receipt.json"
            receipt = eb.validate_candidate(
                repository_root,
                candidate,
                required_head=REQUIRED_HEAD,
                required_tree=REQUIRED_TREE,
            )
            eb_receipt.write_bytes(eb.canonical_bytes(receipt))
            export_root = case_root / "runtime-export"
            export_root.mkdir()
            (export_root / RUNTIME_FILENAME).write_bytes(candidate.read_bytes())
            return candidate, eb_receipt, export_root

        candidate, eb_receipt, export_root = prepare("positive")
        positive = ee.validate_binding(
            repository_root,
            candidate,
            eb_receipt,
            binding,
            export_root,
            GUEST_RUNTIME_ROOT,
            required_head=REQUIRED_HEAD,
            required_tree=REQUIRED_TREE,
        )
        positive_verification = ee.verify_receipt_envelope(repository_root, positive)

        missing_raw = _write_harness(
            temporary_path / "missing-raw.py",
            'CONTINUATION_MANIFEST_PATH = Path("/mnt/g77-evidence/input.json")\n',
        )
        cases.append(_case(
            "MISSING_RAW_ROOT",
            "HARNESS_EXPECTED_PATH_DECLARATION_MISSING",
            lambda: require_unambiguous_static_declarations(missing_raw, ee),
        ))

        missing_manifest = _write_harness(
            temporary_path / "missing-manifest.py",
            'RAW_ROOT = Path("/mnt/g77-evidence")\n',
        )
        cases.append(_case(
            "MISSING_CONTINUATION_MANIFEST_PATH",
            "HARNESS_EXPECTED_PATH_DECLARATION_MISSING",
            lambda: require_unambiguous_static_declarations(missing_manifest, ee),
        ))

        dynamic_raw = _write_harness(
            temporary_path / "dynamic-raw.py",
            'CONTINUATION_MANIFEST_PATH = Path("/mnt/g77-evidence/input.json")\n'
            'def configure():\n    RAW_ROOT = Path("/mnt/g77-evidence")\n',
        )
        cases.append(_case(
            "DYNAMIC_ONLY_RAW_ROOT",
            "HARNESS_EXPECTED_PATH_DECLARATION_MISSING",
            lambda: require_unambiguous_static_declarations(dynamic_raw, ee),
        ))

        dynamic_manifest = _write_harness(
            temporary_path / "dynamic-manifest.py",
            'RAW_ROOT = Path("/mnt/g77-evidence")\n'
            'def configure():\n    CONTINUATION_MANIFEST_PATH = RAW_ROOT / "input.json"\n',
        )
        cases.append(_case(
            "DYNAMIC_ONLY_CONTINUATION_MANIFEST_PATH",
            "HARNESS_EXPECTED_PATH_DECLARATION_MISSING",
            lambda: require_unambiguous_static_declarations(dynamic_manifest, ee),
        ))

        mismatch_harness = _write_harness(
            temporary_path / "declared-mismatch.py",
            'RAW_ROOT = Path("/mnt/g77-evidence")\n'
            'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "different.json"\n',
        )
        mismatch_candidate, mismatch_eb, mismatch_export = prepare("declared_path_mismatch")
        cases.append(_case(
            "DECLARED_PATH_MISMATCH",
            "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
            lambda: ee.validate_binding(
                repository_root, mismatch_candidate, mismatch_eb, mismatch_harness,
                mismatch_export, GUEST_RUNTIME_ROOT,
                required_head=REQUIRED_HEAD, required_tree=REQUIRED_TREE,
            ),
        ))

        mutation_harness = _write_harness(
            temporary_path / "path-mutation.py",
            'RAW_ROOT = Path("/mnt/g77-evidence")\n'
            f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{RUNTIME_FILENAME}"\n',
        )
        mutation_candidate, mutation_eb, mutation_export = prepare("path_mutation")
        mutation_receipt = ee.validate_binding(
            repository_root, mutation_candidate, mutation_eb, mutation_harness,
            mutation_export, GUEST_RUNTIME_ROOT,
            required_head=REQUIRED_HEAD, required_tree=REQUIRED_TREE,
        )
        mutation_harness.write_text(
            mutation_harness.read_text(encoding="utf-8") + "# unexpected mutation\n",
            encoding="utf-8",
        )
        cases.append(_case(
            "UNEXPECTED_PATH_MUTATION",
            "HARNESS_FILE_SHA256_MISMATCH",
            lambda: ee.verify_receipt_envelope(repository_root, mutation_receipt),
        ))

        changed_candidate, changed_eb, changed_export = prepare("candidate_hash_mismatch")
        changed_envelope = json.loads(changed_candidate.read_bytes())
        changed_envelope["manifest"]["observations"].append("POST_EB_CANDIDATE_MUTATION")
        _rehash_manifest(changed_envelope, du)
        changed_candidate.write_bytes(du.canonical_bytes(changed_envelope))
        cases.append(_case(
            "CANDIDATE_HASH_MISMATCH",
            "CANDIDATE_FILE_SHA256_MISMATCH",
            lambda: ee.validate_binding(
                repository_root, changed_candidate, changed_eb, binding, changed_export,
                GUEST_RUNTIME_ROOT, required_head=REQUIRED_HEAD, required_tree=REQUIRED_TREE,
            ),
        ))

        wrong_manifest_candidate, wrong_manifest_eb, wrong_manifest_export = prepare(
            "wrong_manifest_identity"
        )
        wrong_manifest_path = wrong_manifest_export / RUNTIME_FILENAME
        wrong_manifest = json.loads(wrong_manifest_path.read_bytes())
        wrong_manifest["schema_id"] = "WRONG_CONTINUATION_MANIFEST_ENVELOPE_IDENTITY"
        wrong_manifest_path.write_bytes(canonical_bytes(wrong_manifest))
        cases.append(_case(
            "WRONG_MANIFEST_IDENTITY",
            "RUNTIME_BYTES_DIFFER",
            lambda: ee.validate_binding(
                repository_root, wrong_manifest_candidate, wrong_manifest_eb, binding,
                wrong_manifest_export, GUEST_RUNTIME_ROOT,
                required_head=REQUIRED_HEAD, required_tree=REQUIRED_TREE,
            ),
        ))

        wrong_generation_candidate, wrong_generation_eb, wrong_generation_export = prepare(
            "wrong_generation_identity"
        )
        wrong_generation_path = wrong_generation_export / RUNTIME_FILENAME
        wrong_generation = json.loads(wrong_generation_path.read_bytes())
        wrong_generation["manifest"]["generation_identity"] = "WRONG_GENERATION_IDENTITY"
        _rehash_manifest(wrong_generation, du)
        wrong_generation_path.write_bytes(du.canonical_bytes(wrong_generation))
        cases.append(_case(
            "WRONG_GENERATION_IDENTITY",
            "RUNTIME_BYTES_DIFFER",
            lambda: ee.validate_binding(
                repository_root, wrong_generation_candidate, wrong_generation_eb, binding,
                wrong_generation_export, GUEST_RUNTIME_ROOT,
                required_head=REQUIRED_HEAD, required_tree=REQUIRED_TREE,
            ),
        ))

        malformed = _write_harness(
            temporary_path / "malformed.py",
            'RAW_ROOT = Path("/mnt/g77-evidence")\n'
            'CONTINUATION_MANIFEST_PATH = runtime_path_from_environment()\n',
        )
        cases.append(_case(
            "MALFORMED_STATIC_DECLARATION",
            "HARNESS_PATH_DECLARATION_UNSUPPORTED",
            lambda: require_unambiguous_static_declarations(malformed, ee),
        ))

        duplicate = _write_harness(
            temporary_path / "duplicate.py",
            'RAW_ROOT = Path("/mnt/g77-evidence")\n'
            'RAW_ROOT = Path("/mnt/ambiguous")\n'
            'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "input.json"\n',
        )
        cases.append(_case(
            "DUPLICATE_OR_AMBIGUOUS_DECLARATION",
            "DUPLICATE_OR_AMBIGUOUS_STATIC_DECLARATION",
            lambda: require_unambiguous_static_declarations(duplicate, ee),
        ))

    all_negative_pass = all(item["result"] == "PASS" for item in cases)
    positive_pass = all(value == "PASS" for value in positive_verification.values())
    overall = "PASS" if positive_pass and all_negative_pass else "FAIL"
    return {
        "schema_id": "G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_REGRESSION_EVIDENCE_V1",
        "generation_identity": GENERATION_IDENTITY,
        "required_head": REQUIRED_HEAD,
        "required_tree": REQUIRED_TREE,
        "binding_fixture": {
            "path": BINDING_RELATIVE_PATH,
            "sha256": sha256_path(binding),
            "raw_root": str(runtime_root),
            "continuation_manifest_path": str(runtime_path),
            "static_raw_root_declaration": "AUTHENTICATABLE",
            "static_continuation_manifest_path_declaration": "AUTHENTICATABLE",
        },
        "reused_implementations": [
            {"identity": "DU", "path": DU_RELATIVE_PATH, "sha256": DU_SHA256},
            {"identity": "EB", "path": EB_RELATIVE_PATH, "sha256": EB_SHA256},
            {"identity": "EE", "path": EE_RELATIVE_PATH, "sha256": EE_SHA256},
        ],
        "positive_fixture_class": "TRANSIENT_NON_OPERATIONAL_SYNTHETIC_FUTURE_REPRESENTATION",
        "positive_fixture_persisted": False,
        "positive_result": positive_verification,
        "ee_runtime_consumer_binding": "PASS_FOR_REPOSITORY_PRECONDITION",
        "negative_case_count": len(cases),
        "negative_cases": cases,
        "all_negative_cases_fail_closed": all_negative_pass,
        "temporary_regression_residue_count": 0 if not temporary_path.exists() else 1,
        "materialization_count": 0,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "qemu_execution_count": 0,
        "p11_operational_invocation_count": 0,
        "e05_case_execution_count": 0,
        "protected_effect_count": 0,
        "p12_entry_count": 0,
        "production_route_count": 0,
        "candidate_fixture_is_authority": False,
        "auto_continuable": False,
        "overall_result": overall,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = run(args.repo_root.resolve())
    except Exception as exc:
        print(canonical_bytes({
            "schema_id": "G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_REGRESSION_FAILURE_V1",
            "failure_code": getattr(exc, "code", type(exc).__name__),
            "overall_result": "FAIL_CLOSED",
        }).decode(), end="")
        return 1
    print(canonical_bytes(result).decode(), end="")
    return 0 if result["overall_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
