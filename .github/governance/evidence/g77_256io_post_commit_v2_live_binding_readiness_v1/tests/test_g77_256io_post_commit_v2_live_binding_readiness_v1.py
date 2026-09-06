from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Iterator

import jsonschema
import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IO_ROOT = ROOT / ".github/governance/evidence/g77_256io_post_commit_v2_live_binding_readiness_v1"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


IO = load("g77_256io_gate", IO_ROOT / "analysis/G77_256IO_POST_COMMIT_V2_READINESS_FORMALIZER_V1.py")
DU = load("g77_256io_du", ROOT / IO.DU_VALIDATOR)
EB = load("g77_256io_eb", ROOT / IO.EB_VALIDATOR)
EE = load("g77_256io_ee", ROOT / IO.EE_VALIDATOR)
REPORT = IO_ROOT / "G77_256IO_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = IO_ROOT / "G77_256IO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"


@contextmanager
def assets() -> Iterator[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix=".g77_256io_test_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(DU.canonical_bytes(DU.build_du_fixture(ROOT)))
        eb_envelope = EB.validate_candidate(ROOT, candidate)
        eb_path = temporary / "eb-v2.json"
        eb_path.write_bytes(EB.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / "G77_256EC_CONTINUATION_MANIFEST_V1.json").write_bytes(candidate.read_bytes())
        harness = ROOT / ".github/governance/evidence/g77_256ec_p11_operational_v1/harness/G77_256EC_P11_OPERATIONAL_HARNESS_V1.py"
        ee_envelope = EE.validate_binding(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
        yield {
            "candidate": candidate, "eb": eb_envelope, "eb_path": eb_path,
            "runtime": runtime, "harness": harness, "ee": ee_envelope,
        }


def rehash(module: Any, envelope: dict[str, Any]) -> None:
    envelope["receipt_inner_sha256"] = module.sha256_bytes(
        module.canonical_bytes(envelope["receipt"])
    )


def test_exact_committed_in_entry_ancestry_nested_and_scope() -> None:
    entry = IO.authenticate_entry(ROOT)
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (
        IO.IN_HEAD, IO.IN_TREE, IO.IN_HEAD
    )
    assert entry["nested_authority"]["head"] == IO.NESTED_HEAD
    assert IO.authenticate_worktree_scope(ROOT)["file_count"] == 9


def test_exact_in_reconstruction_and_inner_seal() -> None:
    result = IO.reconstruct_in(ROOT)
    assert result["status"] == "VERIFIED"
    assert result["artifact_count"] == 4
    assert result["inner_seal"] == "VERIFIED"


def test_six_v2_owners_committed_at_in_and_bounded_repair_scope() -> None:
    result = IO.authenticate_v2_owners(ROOT)
    assert result["committed_owner_count"] == 6
    assert result["repair_owner_count"] == 5
    assert sum(item["io_repair"] for item in result["identities"].values()) == 5


def test_v1_owner_bytes_immutable() -> None:
    assert {path: IO.sha256_path(ROOT / path) for path in IO.V1_HASHES} == IO.V1_HASHES


def test_du_fixture_derives_authenticated_if_target() -> None:
    envelope = DU.build_du_fixture(ROOT)
    assert envelope["manifest"]["required_head"] == IO.IF_HEAD
    assert envelope["manifest"]["source_tree"] == IO.IF_TREE
    assert set(DU.validate_envelope(envelope, ROOT, expected_head=IO.IF_HEAD).values()) == {"PASS"}


def test_runtime_target_is_launcher_context_and_git_authenticated() -> None:
    target = EB._authenticated_runtime_target(ROOT)
    assert (target["head"], target["tree"]) == (IO.IF_HEAD, IO.IF_TREE)
    assert subprocess.check_output(
        ["git", "rev-parse", f"{target['head']}^{{tree}}"], cwd=ROOT, text=True
    ).strip() == target["tree"]


def test_eb_v2_live_binding_separates_target_from_current_baseline() -> None:
    with assets() as value:
        receipt = value["eb"]["receipt"]
        assert receipt["runtime_target_selection_binding"]["head"] == IO.IF_HEAD
        assert receipt["certification_baseline"] == {"head": IO.IN_HEAD, "tree": IO.IN_TREE}
        assert receipt["runtime_target_selection_binding"]["head"] != receipt["certification_baseline"]["head"]
        assert EB.verify_receipt_envelope(ROOT, value["eb"])["overall_result"] == "PASS"


def test_ee_v2_live_binding_and_eb_ee_coherence() -> None:
    with assets() as value:
        eb_receipt = value["eb"]["receipt"]
        ee_receipt = value["ee"]["receipt"]
        assert eb_receipt["certification_baseline"] == ee_receipt["certification_baseline"]
        assert eb_receipt["runtime_target_selection_binding"] == ee_receipt["runtime_target_selection_binding"]
        result = EE.verify_receipt_envelope(ROOT, value["ee"])
        assert result["pre_materialization_runtime_path_binding_result"] == "PASS"


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ({"head": "0" * 40}, "CERTIFICATION_BASELINE_COMMIT_NONEXISTENT"),
        ({"tree": "0" * 40}, "CERTIFICATION_BASELINE_TREE_MISMATCH"),
        ({"branch": "FORBIDDEN"}, "UNKNOWN_RECEIPT_FIELD"),
        ({"head": IO.IF_HEAD, "tree": IO.IF_TREE}, "CERTIFICATION_BASELINE_STALE"),
    ],
)
def test_eb_invalid_or_if_substituted_certification_baseline_rejects(
    mutation: dict[str, str], expected: str
) -> None:
    with assets() as value:
        receipt = deepcopy(value["eb"])
        receipt["receipt"]["certification_baseline"].update(mutation)
        rehash(EB, receipt)
        with pytest.raises(EB.ReceiptError) as caught:
            EB.verify_receipt_envelope(ROOT, receipt)
        assert caught.value.code == expected


def test_caller_selected_or_arbitrary_runtime_target_receipt_rejects() -> None:
    with assets() as value:
        receipt = deepcopy(value["eb"])
        receipt["receipt"]["runtime_target_selection_binding"].update(
            {"head": IO.IN_HEAD, "tree": IO.IN_TREE}
        )
        rehash(EB, receipt)
        with pytest.raises(EB.ReceiptError) as caught:
            EB.verify_receipt_envelope(ROOT, receipt)
        assert caught.value.code == "RUNTIME_TARGET_SELECTION_BINDING_MISMATCH"


def test_candidate_bound_to_current_in_instead_of_if_rejects() -> None:
    with tempfile.TemporaryDirectory(prefix=".g77_256io_wrong_target_", dir=ROOT) as raw:
        candidate = Path(raw) / "candidate.json"
        envelope = DU.build_du_fixture(ROOT)
        envelope["manifest"]["required_head"] = IO.IN_HEAD
        envelope["manifest"]["source_tree"] = IO.IN_TREE
        envelope["manifest_sha256"] = DU.sha256_bytes(DU.canonical_bytes(envelope["manifest"]))
        candidate.write_bytes(DU.canonical_bytes(envelope))
        with pytest.raises(EB.ReceiptError) as caught:
            EB.validate_candidate(ROOT, candidate)
        assert caught.value.code == "REQUIRED_HEAD_MISMATCH"


def test_ee_runtime_target_receipt_substitution_rejects() -> None:
    with assets() as value:
        receipt = deepcopy(value["ee"])
        receipt["receipt"]["runtime_target_selection_binding"]["head"] = IO.IN_HEAD
        rehash(EE, receipt)
        with pytest.raises(EE.BindingError) as caught:
            EE.verify_receipt_envelope(ROOT, receipt)
        assert caught.value.code == "RUNTIME_TARGET_SELECTION_BINDING_MISMATCH"


def test_v2_receipt_schemas_are_closed_and_accept_live_receipts() -> None:
    with assets() as value:
        eb_schema = json.loads((ROOT / IO.EB_SCHEMA).read_bytes())
        ee_schema = json.loads((ROOT / IO.EE_SCHEMA).read_bytes())
        jsonschema.Draft202012Validator.check_schema(eb_schema)
        jsonschema.Draft202012Validator.check_schema(ee_schema)
        jsonschema.Draft202012Validator(eb_schema).validate(value["eb"])
        jsonschema.Draft202012Validator(ee_schema).validate(value["ee"])
        bad = deepcopy(value["eb"])
        bad["receipt"]["unknown"] = True
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(eb_schema).validate(bad)


@pytest.mark.parametrize("module", [DU, EB, EE])
def test_family_local_v1_v2_dispatch_remains_exact_and_unknown_rejects(module: Any) -> None:
    assert module.V1_CONTRACT_TUPLE["version"] == "1.0.0"
    assert module.V2_CONTRACT_TUPLE["version"] == "2.0.0"
    unknown = dict(module.V2_CONTRACT_TUPLE)
    unknown["version"] = "3.0.0"
    function = module.dispatch_validate if module is DU else module.dispatch_verify_receipt
    with pytest.raises(Exception) as caught:
        if module is DU:
            function({}, ROOT, contract_tuple=unknown)
        else:
            function(ROOT, {}, contract_tuple=unknown)
    assert getattr(caught.value, "code", "") == "DISPATCH_TUPLE_UNKNOWN"


def test_terminal_is_canonical_duplicate_safe_inner_sealed_and_replayable() -> None:
    envelope = IO.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == IO.sha256_bytes(
        IO.canonical_bytes(envelope["reduction"])
    )
    assert envelope == IO.terminal_envelope(ROOT)
    raw = TERMINAL.read_text()
    with pytest.raises(IO.IOGateError):
        IO._unique([("schema_id", 1), ("schema_id", 2)])
    assert raw.endswith("\n")


def test_g48_has_exactly_six_top_level_headings() -> None:
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]


def test_terminal_a_operational_zero_and_e05_unchanged() -> None:
    reduction = IO.terminal_reduction(ROOT)
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8}
    assert reduction["terminal"]["terminal"] == "A__READINESS_VERIFIED"
    assert reduction["terminal"]["future_preoperational_readiness"] == "VERIFIED"
    assert reduction["terminal"]["future_operational_capability"].startswith("NOT_PROVEN")
    assert reduction["terminal"]["auto_continuable"] is False


def test_no_precommit_self_reference_or_future_io_commit_prediction() -> None:
    text = REPORT.read_text() + (IO_ROOT / "analysis/G77_256IO_POST_COMMIT_V2_READINESS_FORMALIZER_V1.py").read_text()
    assert "future IO commit" not in text.lower()
    reduction = IO.terminal_reduction(ROOT)
    assert reduction["live_binding"]["certification_baseline"] == {"head": IO.IN_HEAD, "tree": IO.IN_TREE}
