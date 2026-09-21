"""Synthetic, non-authoritative Step71 contract and durability proof."""
from copy import deepcopy
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from aigol.runtime import step69_governance_clarification_binding_v1 as binding
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


def payload(outcome="APPROVAL"):
    result = dict(binding.FIXED)
    result.update(human_outcome=outcome,
                  human_acknowledgement="SYNTHETIC_NON_AUTHORITATIVE acknowledgement",
                  channel_provenance_policy="SYNTHETIC_NON_AUTHORITATIVE channel policy",
                  target_revision_policy="SYNTHETIC_NON_AUTHORITATIVE revision policy")
    response = outcome + "\n" + result["human_acknowledgement"]
    result["human_decision_evidence"] = {
        "decision_reference": "synthetic://step71/decision",
        "actor_identity": "SYNTHETIC_NON_AUTHORITATIVE_ACTOR",
        "session_identity": "SYNTHETIC_NON_AUTHORITATIVE_SESSION",
        "presentation_reference": "synthetic://step71/presentation",
        "exact_human_response": response,
        "response_digest": replay_hash(response),
        "decision_payload_digest": replay_hash(result),
    }
    return result


@pytest.mark.parametrize("outcome", sorted(binding.OUTCOMES))
def test_closed_outcomes_and_no_effect(outcome):
    record = binding.create_step69_clarification_record_v1(payload(outcome))
    assert binding.validate_step69_clarification_record_v1(record) == record
    for key, value in binding.FIXED.items():
        assert record[key] == value
    assert not any("authority_act" in key or "continuation" in key for key in record)


@pytest.mark.parametrize("field", sorted(binding.PAYLOAD_FIELDS))
def test_missing_field(field):
    data = payload()
    del data[field]
    with pytest.raises(FailClosedRuntimeError):
        binding.create_step69_clarification_record_v1(data)


@pytest.mark.parametrize("field", sorted(binding.FIXED))
def test_wrong_fixed_binding_or_effect(field):
    data = payload()
    data[field] = True if type(data[field]) is bool else "WRONG_SCOPE"
    with pytest.raises(FailClosedRuntimeError):
        binding.create_step69_clarification_record_v1(data)


@pytest.mark.parametrize("field", binding.TEXT_FIELDS)
@pytest.mark.parametrize("value", [None, "", "   ", {}, [], False])
def test_malformed_decision_or_policy_text(field, value):
    data = payload()
    data[field] = value
    with pytest.raises(FailClosedRuntimeError):
        binding.create_step69_clarification_record_v1(data)


@pytest.mark.parametrize("field", sorted(binding.PAYLOAD_FIELDS | {"extra"}))
def test_exact_record_schema(field):
    record = binding.create_step69_clarification_record_v1(payload())
    if field == "extra":
        record[field] = "extra"
    else:
        del record[field]
    with pytest.raises(FailClosedRuntimeError):
        binding.validate_step69_clarification_record_v1(record)


def test_extra_payload_invalid_outcome_and_boolean_type():
    for field, value in (("extra", 1), ("human_outcome", "AUTO"), ("g70_authorized", 0)):
        data = payload()
        data[field] = value
        with pytest.raises(FailClosedRuntimeError):
            binding.create_step69_clarification_record_v1(data)


@pytest.mark.parametrize("field", sorted(set(binding.EVIDENCE_TEXT_FIELDS) | {"response_digest", "decision_payload_digest"}))
def test_missing_evidence_binding(field):
    data = payload()
    del data["human_decision_evidence"][field]
    with pytest.raises(FailClosedRuntimeError):
        binding.create_step69_clarification_record_v1(data)


@pytest.mark.parametrize("field", ["human_outcome", "human_acknowledgement", "channel_provenance_policy", "target_revision_policy"])
def test_changed_decision_cannot_reuse_evidence_digest(field):
    data = payload()
    data[field] = "REJECT" if field == "human_outcome" else "changed"
    with pytest.raises(FailClosedRuntimeError):
        binding.create_step69_clarification_record_v1(data)


def test_response_binding_and_evidence_schema():
    for change in ({"exact_human_response": "unrelated"}, {"response_digest": "sha256:bad"}, {"extra": "x"}):
        data = payload()
        data["human_decision_evidence"].update(change)
        with pytest.raises(FailClosedRuntimeError):
            binding.create_step69_clarification_record_v1(data)


def test_identity_digest_and_canonical_bytes(tmp_path):
    data = payload()
    record = binding.create_step69_clarification_record_v1(data)
    reordered = binding.create_step69_clarification_record_v1(dict(reversed(list(data.items()))))
    assert record == reordered
    assert canonical_serialize(record) == canonical_serialize(reordered)
    seed = {key: value for key, value in record.items() if key != "record_digest"}
    assert record["record_digest"] == replay_hash(seed)
    path = binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
    assert path.read_bytes() == (canonical_serialize(record) + "\n").encode()
    assert binding.read_step69_clarification_record_v1(storage_root=tmp_path) == record
    old_stat = path.stat()
    assert binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record) == path
    assert path.stat().st_ino == old_stat.st_ino
    assert path.stat().st_mtime_ns == old_stat.st_mtime_ns
    assert len(list(path.parent.iterdir())) == 1


@pytest.mark.parametrize("field", ["human_outcome", "human_acknowledgement", "channel_provenance_policy", "target_revision_policy"])
def test_divergent_same_identity_never_overwrites(tmp_path, field):
    first = binding.create_step69_clarification_record_v1(payload())
    path = binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=first)
    original = path.read_bytes()
    data = payload("REJECT") if field == "human_outcome" else payload()
    if field != "human_outcome":
        data[field] += " changed"
        response = data["human_outcome"] + "\n" + data["human_acknowledgement"]
        data["human_decision_evidence"]["exact_human_response"] = response
        data["human_decision_evidence"]["response_digest"] = replay_hash(response)
        data["human_decision_evidence"]["decision_payload_digest"] = replay_hash({k: v for k, v in data.items() if k != "human_decision_evidence"})
    second = binding.create_step69_clarification_record_v1(data)
    assert first["record_identity"] == second["record_identity"]
    with pytest.raises(FailClosedRuntimeError):
        binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=second)
    assert path.read_bytes() == original


@pytest.mark.parametrize("corruption", ["digest", "identity", "noncanonical", "malformed", "duplicate_key"])
def test_corruption_readback_fails_closed(tmp_path, corruption):
    record = binding.create_step69_clarification_record_v1(payload())
    path = binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
    if corruption in {"digest", "identity"}:
        record["record_" + corruption] = "wrong"
        text = canonical_serialize(record) + "\n"
    elif corruption == "noncanonical":
        text = json.dumps(record, indent=2)
    elif corruption == "duplicate_key":
        text = '{"step":"STEP69",' + canonical_serialize(record)[1:] + "\n"
    else:
        text = "broken"
    path.write_text(text)
    with pytest.raises(FailClosedRuntimeError):
        binding.read_step69_clarification_record_v1(storage_root=tmp_path)


@pytest.mark.parametrize("artifact", [
    {"artifact_type": "STEP46_CONSTITUTIONAL_POLICY_DEFINITION_DECISION_ARTIFACT_V1"},
    {"record_contract_version": "STEP46_COMPLETE_OWNER_ARTIFACT_EVIDENCE_RECORD_V1"},
])
def test_wrong_scope_artifacts_rejected(tmp_path, artifact):
    with pytest.raises(FailClosedRuntimeError):
        binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=artifact)
    assert not list(tmp_path.iterdir())


def test_concurrent_identical_publication(tmp_path):
    record = binding.create_step69_clarification_record_v1(payload())
    with ThreadPoolExecutor(max_workers=4) as pool:
        paths = list(pool.map(lambda _: binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record), range(4)))
    assert len(set(paths)) == 1
    assert binding.read_step69_clarification_record_v1(storage_root=tmp_path) == record
    assert len(list(paths[0].parent.iterdir())) == 1


@pytest.mark.parametrize("operation", ["link", "fsync"])
def test_publication_failure_has_no_success_receipt(tmp_path, monkeypatch, operation):
    record = binding.create_step69_clarification_record_v1(payload())
    def fail(*args):
        raise OSError("synthetic failure")
    monkeypatch.setattr(binding.os, operation, fail)
    with pytest.raises(FailClosedRuntimeError):
        binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
    assert not list(tmp_path.rglob("*.json"))
    assert not list(tmp_path.rglob("*.tmp"))


def test_directory_sync_failure_then_identical_retry(tmp_path, monkeypatch):
    record = binding.create_step69_clarification_record_v1(payload())
    original = binding.os.fsync
    calls = []
    def fail_third(fd):
        calls.append(fd)
        if len(calls) == 3:
            raise OSError("synthetic directory sync failure")
        original(fd)
    monkeypatch.setattr(binding.os, "fsync", fail_third)
    with pytest.raises(FailClosedRuntimeError):
        binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
    assert len(list(tmp_path.rglob("*.json"))) == 1
    monkeypatch.setattr(binding.os, "fsync", original)
    binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
    assert binding.read_step69_clarification_record_v1(storage_root=tmp_path) == record


def test_missing_and_symlink_readback_rejected(tmp_path):
    with pytest.raises(FailClosedRuntimeError):
        binding.read_step69_clarification_record_v1(storage_root=tmp_path)
    record = binding.create_step69_clarification_record_v1(payload())
    path = binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
    target = tmp_path / "synthetic-copy"
    path.rename(target)
    path.symlink_to(target)
    with pytest.raises(FailClosedRuntimeError):
        binding.persist_step69_clarification_record_v1(storage_root=tmp_path, record=record)
