from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
LC = ROOT / ".github/governance/evidence/g77_256lc_expired_bootstrap_digest_projection_reissue_v1"
FORMALIZER = LC / "analysis/G77_256LC_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_FORMALIZER_V1.py"
REPORT = LC / "G77_256LC_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = LC / "G77_256LC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

spec = importlib.util.spec_from_file_location("g77_256lc_formalizer", FORMALIZER)
assert spec is not None and spec.loader is not None
formalizer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = formalizer
spec.loader.exec_module(formalizer)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_reduction() -> dict:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == formalizer.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        formalizer.canonical_bytes(reduction)
    ).hexdigest()
    return reduction


def test_exact_current_source_to_asset_hash_chain() -> None:
    trace = formalizer.authenticate_minimum_delta()
    assert trace["source_bytes_sha256"] == formalizer.JR_SHA256
    assert trace["current_fm_expected_sha256"] == formalizer.JR_SHA256
    assert trace["current_cloud_init_presented_sha256"] == formalizer.JR_SHA256
    assert trace["current_nocloud_user_data_sha256"] == formalizer.CLOUD_AFTER_SHA256
    assert trace["current_nocloud_image_sha256"] == formalizer.SEED_AFTER_SHA256
    assert sha256(formalizer.META) == formalizer.META_SHA256
    assert sha256(formalizer.NETWORK) == formalizer.NETWORK_SHA256


def test_dirty_production_delta_is_exact_three_existing_owner_files() -> None:
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", formalizer.ENTRY_HEAD], cwd=ROOT, text=True
    ).splitlines()
    production_changed = [
        path
        for path in changed
        if not path.startswith(formalizer.LC.relative_to(ROOT).as_posix() + "/")
    ]
    assert production_changed == sorted(
        [
            formalizer.FM.relative_to(ROOT).as_posix(),
            formalizer.CLOUD.relative_to(ROOT).as_posix(),
            formalizer.SEED.relative_to(ROOT).as_posix(),
        ]
    )
    assert formalizer.FM.read_bytes() == formalizer.committed(formalizer.FM).replace(
        formalizer.CLOUD_BEFORE_SHA256.encode(), formalizer.CLOUD_AFTER_SHA256.encode()
    ).replace(
        formalizer.SEED_BEFORE_SHA256.encode(), formalizer.SEED_AFTER_SHA256.encode()
    )
    assert formalizer.CLOUD.read_bytes() == formalizer.committed(formalizer.CLOUD).replace(
        b"f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
        formalizer.JR_SHA256.encode(),
    )


def test_authenticated_nocloud_contract_uses_projection_and_digest_rebind() -> None:
    proof = formalizer.authenticate_seed_generation_contract()
    assert proof["image_byte_identity_required"] is False
    assert proof["user_data_byte_identity_required"] is True
    assert proof["image_digest_rebinding_allowed"] is True
    assert proof["normalization_allowed"] is False
    assert proof["semantic_content_impact"] == "VERIFIED__NONE__ALL_THREE_PROJECTED_MEMBERS_BYTE_EXACT"
    assert proof["seed_sha256"] == formalizer.SEED_AFTER_SHA256


def test_fm_change_is_hash_rebind_only_and_p11_is_unchanged() -> None:
    before = formalizer.committed(formalizer.FM)
    after = formalizer.FM.read_bytes()
    assert before.count(formalizer.CLOUD_BEFORE_SHA256.encode()) == 1
    assert before.count(formalizer.SEED_BEFORE_SHA256.encode()) == 1
    assert after.count(formalizer.CLOUD_AFTER_SHA256.encode()) == 1
    assert after.count(formalizer.SEED_AFTER_SHA256.encode()) == 1
    assert sha256(formalizer.P11) == formalizer.P11_SHA256
    tree = ast.parse(after.decode("utf-8"))
    assert sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in tree.body
    ) == 1


def test_authority_free_static_readiness_passes_without_operation(tmp_path: Path) -> None:
    readiness = formalizer.authenticate_full_static_readiness(tmp_path)
    assert readiness["result"] == "STATIC_READINESS_PASS"
    assert readiness["fixture_class"] == "TEST_ONLY__NONAUTHORITY__NONOPERATIONAL__NO_REQUEST"
    assert readiness["human_operational_authorization_count"] == 0
    assert readiness["qemu_execution_count"] == 0
    assert readiness["automatic_retry_count"] == 0
    assert readiness["repair_retry_count"] == 0
    assert readiness["replay_count"] == 0


def test_terminal_reduction_is_canonical_sealed_and_fail_closed() -> None:
    reduction = load_reduction()
    assert reduction["generation"] == "G77-256LC"
    assert reduction["generation_identity"] == formalizer.GENERATION_IDENTITY
    assert reduction["classification"]["failure_class"] == "HARNESS_OR_TEST_ARTIFACT"
    assert reduction["frontier"]["static_pre_operational_chain_complete"] == "VERIFIED__WITHIN_AUTHENTICATED_STATIC_SCOPE"
    assert reduction["frontier"]["fresh_operational_attempt_readiness"] == "READY__REPOSITORY_ONLY"
    assert reduction["e05"]["state"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["current_generation_credit"] == "VERIFIED__0"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_cross_vector_scope_and_architecture_are_bounded() -> None:
    reduction = load_reduction()
    cross = reduction["cross_vector_reuse_assessment"]
    assert cross["affected_vectors"] == ["EXPIRED"]
    assert cross["unaffected_vectors"] == [
        "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"
    ]
    architecture = reduction["architecture"]
    assert architecture["production_mutation"] == 3
    assert architecture["p11_mutation"] == 0
    assert architecture["new_owner"] == 0
    assert architecture["new_route"] == 0
    assert architecture["new_generic_abstraction"] == 0
    assert architecture["production_route"] == "1_TO_1"


def test_g48_report_has_exact_six_h1_and_five_ria_questions() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
    assert report.rstrip().endswith(formalizer.TERMINAL + "`.")
