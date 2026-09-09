from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
JS = ROOT / ".github/governance/evidence/g77_256js_expired_operational_v1"
REDUCTION = JS / "G77_256JS_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json"
MATERIALIZER = JS / "orchestration/G77_256JS_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCER = JS / "analysis/G77_256JS_PREAUTHORIZATION_BLOCKER_REDUCER_V1.py"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def load_reduction() -> dict:
    envelope = json.loads(REDUCTION.read_bytes())
    assert envelope["reduction_sha256"] == hashlib.sha256(
        canonical_bytes(envelope["reduction"])
    ).hexdigest()
    return envelope["reduction"]


def test_exact_blocker_is_only_checkout_head_tree_pair() -> None:
    reduction = load_reduction()
    blocker = reduction["blocker"]
    assert reduction["terminal"] == (
        "M__EXPIRED_FRESH_PREAUTHORIZATION_BOOTSTRAP_HEAD_TREE_BINDING_MISMATCH"
    )
    assert blocker["differing_tuple_positions"] == [2, 3]
    expected = blocker["expected_argument_tuple"]
    observed = blocker["observed_argument_tuple"]
    assert expected[:2] == observed[:2]
    assert expected[4] == observed[4]
    assert expected[2:4] == [
        "304b342e26e92f226afa01db4b4203acfa51f532",
        "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937",
    ]
    assert observed[2:4] == [
        "f2f00fab5b47e5c3e59629f9542258e65f20a9c0",
        "07ae3ad87775f30f298a691f1054881915604d32",
    ]


def test_exact_expired_candidate_and_temporal_binding_survived() -> None:
    candidate = load_reduction()["candidate"]
    assert candidate["candidate_sha256"] == (
        "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
    )
    assert candidate["expired_adapter_sha256"] == (
        "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
    )
    assert candidate["valid_from_unix_ns"] == 100
    assert candidate["valid_until_unix_ns"] == 1000
    assert candidate["governed_preclaim_coordinate_unix_ns"] == 1000
    assert candidate["request_identity"] == "NOT_MATERIALIZED"
    assert candidate["presentation_identity"] == "NOT_MATERIALIZED"
    assert candidate["preauthorization_checkpoint_digest"] == "NOT_MATERIALIZED"


def test_authority_operation_and_credit_remain_zero() -> None:
    reduction = load_reduction()
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["e05"] == {
        "after": "VERIFIED__11_OF_18",
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True
    forbidden = (
        JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        JS / "G77_256JS_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        JS / "G77_256JS_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
    )
    assert not any(path.exists() or path.is_symlink() for path in forbidden)


def test_no_production_architecture_delta_or_operational_entry() -> None:
    reduction = load_reduction()
    assert set(reduction["architecture"].values()) <= {
        "VERIFIED__0",
        "VERIFIED__1",
    }
    assert reduction["architecture"]["production_route_before"] == "VERIFIED__1"
    assert reduction["architecture"]["production_route_after"] == "VERIFIED__1"
    assert reduction["architecture"]["production_route_delta"] == "VERIFIED__0"
    tree = ast.parse(MATERIALIZER.read_text(encoding="utf-8"))
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "main" not in calls
    assert "run_qemu" not in calls
    assert "validate_final_admission" not in calls


def test_reducer_and_materializer_parse_and_reuse_existing_owners() -> None:
    ast.parse(MATERIALIZER.read_text(encoding="utf-8"))
    ast.parse(REDUCER.read_text(encoding="utf-8"))
    source = MATERIALIZER.read_text(encoding="utf-8")
    assert "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py" in source
    assert "G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py" in source
    assert "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py" in source
    assert "G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py" in source
