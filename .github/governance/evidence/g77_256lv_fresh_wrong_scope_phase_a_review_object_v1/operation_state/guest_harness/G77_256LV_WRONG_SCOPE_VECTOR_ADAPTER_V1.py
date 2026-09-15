#!/usr/bin/env python3
"""Bound WRONG_SCOPE to the existing FM/FC/ER/P11 route.

This vector-local adapter owns no launcher, authority, P11 behavior, or new
route.  It authenticates LE's committed semantic proof and derives the
existing FC/FK runtime with one independent attempt-time mutation:
``authority_scope``.  Canonical Human-act and CHE identities are recomputed
only as dependent consequences.  Import and specialization are non-operational.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


GUEST_REPOSITORY_ROOT = Path("/mnt/aigol")
GUEST_CONTEXT_PATH = Path("/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
GUEST_PROJECTED_FM_CONTEXT_OWNER = Path(
    "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py"
)
FC_ADAPTER = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_ADAPTER_SHA256 = (
    "b2e9f72d6b35b2db0021bf9bf1223350f570d1eaecda3379a8af013c705aa770"
)
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_HARNESS_SHA256 = (
    "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
)
LE_REDUCTION = Path(
    ".github/governance/evidence/g77_256le_wrong_scope_minimum_governed_delta_v1/"
    "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
LE_REDUCTION_SHA256 = (
    "7710f40b8f2bb57229167c37fff527cf2e18c81769f82db096e029a3895c45dc"
)
LE_TERMINAL = (
    "A__WRONG_SCOPE_EXISTING_CAPABILITY_REUSED__REPOSITORY_PROOF_COMPLETE__"
    "OPERATIONAL_PROOF_REQUIRED"
)
VECTOR = "WRONG_SCOPE"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_SCOPE"
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
EXPECTED_DENIAL = "operational Human act scope is invalid"
EXPECTED_DENIAL_BOUNDARY = (
    "D2_AUTHORITY_SCOPE_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)


class WrongScopeAdapterError(RuntimeError):
    """One fail-closed WRONG_SCOPE specialization error."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongScopeAdapterError(f"OWNER_IMPORT_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_wrong_scope_semantics(repository_root: Path) -> dict[str, Any]:
    """Authenticate LE's sealed WRONG_SCOPE model without caller substitutions."""

    path = repository_root.resolve() / LE_REDUCTION
    if path.is_symlink() or not path.is_file() or _sha256(path) != LE_REDUCTION_SHA256:
        raise WrongScopeAdapterError("LE_REDUCTION_BINDING_INVALID")
    envelope = json.loads(path.read_bytes())
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        raise WrongScopeAdapterError("LE_REDUCTION_MISSING")
    if envelope.get("reduction_sha256") != hashlib.sha256(
        _canonical_bytes(reduction)
    ).hexdigest():
        raise WrongScopeAdapterError("LE_REDUCTION_SEAL_INVALID")
    if reduction.get("terminal") != LE_TERMINAL:
        raise WrongScopeAdapterError("LE_TERMINAL_INVALID")
    model = reduction.get("wrong_scope_model")
    required = {
        "vector": VECTOR,
        "canonical_obligation": SELECTED_VECTOR,
        "independent_semantic_mutation_count": 1,
        "independent_semantic_mutation_set": [
            f"authority_scope:{EXPECTED_SCOPE}->{PRESENTED_SCOPE}"
        ],
    }
    if not isinstance(model, dict) or any(
        model.get(field) != expected for field, expected in required.items()
    ):
        raise WrongScopeAdapterError("LE_WRONG_SCOPE_MODEL_DRIFT")
    if model.get("baseline", {}).get("authority_scope") != EXPECTED_SCOPE:
        raise WrongScopeAdapterError("LE_BASELINE_SCOPE_DRIFT")
    if model.get("presented", {}).get("authority_scope") != PRESENTED_SCOPE:
        raise WrongScopeAdapterError("LE_PRESENTED_SCOPE_DRIFT")
    denial = model.get("expected_denial", {})
    if denial.get("reason") != EXPECTED_DENIAL:
        raise WrongScopeAdapterError("LE_DENIAL_REASON_DRIFT")
    return model


def specialize_er_harness(repository_root: Path) -> ModuleType:
    """Preserve host admission while observing the stable runtime checkout."""

    root = repository_root.resolve()
    authenticate_wrong_scope_semantics(root)
    path = root / ER_HARNESS
    if path.is_symlink() or not path.is_file() or _sha256(path) != ER_HARNESS_SHA256:
        raise WrongScopeAdapterError("ER_HARNESS_BINDING_INVALID")
    source = path.read_text(encoding="utf-8")
    collapsed_roles = (
        '    if (\n'
        '        context["repository_head"] != observed_head\n'
        '        or context["repository_tree"] != observed_tree\n'
        '        or checkout_binding["head"] != observed_head\n'
        '        or checkout_binding["tree"] != observed_tree\n'
        '    ):\n'
        '        raise RuntimeError("sealed operation context checkout binding mismatch")\n'
    )
    separated_roles = (
        '    # FM already authenticated the sealed current admission repository.\n'
        '    # Guest observation owns only the distinct stable runtime checkout.\n'
        '    if (\n'
        '        checkout_binding["head"] != observed_head\n'
        '        or checkout_binding["tree"] != observed_tree\n'
        '    ):\n'
        '        raise RuntimeError("sealed operation context checkout binding mismatch")\n'
    )
    if source.count(collapsed_roles) != 1:
        raise WrongScopeAdapterError("ER_REPOSITORY_ROLE_SEPARATION_ANCHOR_INVALID")
    source = source.replace(collapsed_roles, separated_roles)
    module = ModuleType("g77_256lg_wrong_scope_er_specialization")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def specialize_fc_runtime_source(
    *, repository_root: Path, identity_namespace_prefix: str
) -> str:
    """Derive one WRONG_SCOPE strategy from the existing FC family-local shell."""

    root = repository_root.resolve()
    authenticate_wrong_scope_semantics(root)
    source_path = root / FC_ADAPTER
    if source_path.is_symlink() or not source_path.is_file():
        raise WrongScopeAdapterError("FC_ADAPTER_PATH_INVALID")
    if _sha256(source_path) != FC_ADAPTER_SHA256:
        raise WrongScopeAdapterError("FC_ADAPTER_HASH_MISMATCH")
    if not identity_namespace_prefix.startswith("G77_256"):
        raise WrongScopeAdapterError("IDENTITY_NAMESPACE_PREFIX_INVALID")

    source = source_path.read_text(encoding="utf-8")
    transformed = source.replace("G77_256FC", identity_namespace_prefix)
    transformed = transformed.replace("WRONG_ATTEMPT", VECTOR)
    transformed = transformed.replace("wrong_attempt", "wrong_scope")

    scope_constant = (
        f'WRONG_SCOPE_ID = "{identity_namespace_prefix}_E05_SUPPLIED_'
        'WRONG_SCOPE_002"'
    )
    if transformed.count(scope_constant) != 1:
        raise WrongScopeAdapterError("FC_SCOPE_CONSTANT_ANCHOR_INVALID")
    transformed = transformed.replace(
        scope_constant,
        f'WRONG_SCOPE_ID = "{PRESENTED_SCOPE}"',
    )

    metadata_tail = (
        '            "machine_completed_human_semantics": 0,\n'
        "        },\n"
    )
    context_bound_metadata_tail = (
        '            "machine_completed_human_semantics": 0,\n'
        '            "authorized_context_sha256": gate.operation_context_sha256,\n'
        "        },\n"
    )
    if transformed.count(metadata_tail) != 1:
        raise WrongScopeAdapterError("FC_AUTHORIZED_CONTEXT_METADATA_ANCHOR_INVALID")
    transformed = transformed.replace(metadata_tail, context_bound_metadata_tail)

    input_reference_anchor = (
        '        "record_identity": "",\n'
        '        "attempt_identity": AUTHORIZED_ATTEMPT_ID,\n'
    )
    aligned_input_reference = (
        '        "record_identity": "",\n'
        '        "attempt_identity": AUTHORIZED_ATTEMPT_ID,\n'
        '        "authorization_reference": ACT_ID,\n'
    )
    if transformed.count(input_reference_anchor) != 1:
        raise WrongScopeAdapterError("FC_INPUT_AUTHORIZATION_REFERENCE_ANCHOR_INVALID")
    transformed = transformed.replace(input_reference_anchor, aligned_input_reference)

    mutation = (
        "        wrong_value = dict(authorized_record)\n"
        "        wrong_value[\"record_identity\"] = \"\"\n"
        "        wrong_value[\"attempt_identity\"] = WRONG_SCOPE_ID\n"
        "        wrong_bytes = bind_record_identity(wrong_value)\n"
        "        wrong_record = validate_input_record_bytes(wrong_bytes)\n"
        "        differing_fields = sorted(\n"
        "            key for key in authorized_record\n"
        "            if authorized_record[key] != wrong_record[key]\n"
        "        )\n"
    )
    scope_mutation = (
        "        wrong_bytes = authorized_bytes\n"
        "        wrong_record = authorized_record\n"
        "        differing_fields = []\n"
        "        from aigol.runtime.canonical_human_authority_act_contract_v1 import (\n"
        "            CanonicalHumanAuthorityActV1,\n"
        "        )\n"
        "        from aigol.runtime.transport.serialization import replay_hash\n"
        "        wrong_act_value = act.to_dict()\n"
        "        wrong_act_value[\"authority_scope\"] = WRONG_SCOPE_ID\n"
        "        wrong_act = CanonicalHumanAuthorityActV1.from_dict(wrong_act_value)\n"
        "        wrong_correlation = rebind_canonical_correlation(correlation, {\n"
        "            \"source_act_digest\": replay_hash(wrong_act.to_dict()),\n"
        "        })\n"
        "        authority_differing_fields = sorted(\n"
        "            key for key in act.to_dict()\n"
        "            if act.to_dict()[key] != wrong_act.to_dict()[key]\n"
        "        )\n"
        "        correlation_differing_fields = sorted(\n"
        "            key for key in correlation.to_dict()\n"
        "            if correlation.to_dict()[key] != wrong_correlation.to_dict()[key]\n"
        "        )\n"
    )
    if transformed.count(mutation) != 1:
        raise WrongScopeAdapterError("FC_INPUT_MUTATION_ANCHOR_INVALID")
    transformed = transformed.replace(mutation, scope_mutation)

    invocation = (
        "                act=act,\n"
        "                correlation=correlation,\n"
        "                input_record_canonical_bytes=wrong_bytes,\n"
    )
    scope_invocation = (
        "                act=wrong_act,\n"
        "                correlation=wrong_correlation,\n"
        "                input_record_canonical_bytes=wrong_bytes,\n"
    )
    if transformed.count(invocation) != 1:
        raise WrongScopeAdapterError("FC_ATTEMPT_INVOCATION_ANCHOR_INVALID")
    transformed = transformed.replace(invocation, scope_invocation)

    replacements = {
        'denial_error == "operational Human act attempt_identity binding is invalid",': (
            f'denial_error == "{EXPECTED_DENIAL}",'
        ),
        'differing_fields == ["attempt_identity", "record_identity"],': (
            "differing_fields == [],\n"
            '            authority_differing_fields == ["authority_scope"],\n'
            "            correlation_differing_fields == [\n"
            '                "correlation_identity", "source_act_digest",\n'
            "            ],"
        ),
        '"authorized_attempt_identity": AUTHORIZED_ATTEMPT_ID,': (
            f'"authorized_scope": "{EXPECTED_SCOPE}",'
        ),
        '"supplied_attempt_identity": WRONG_SCOPE_ID,': (
            '"presented_scope": WRONG_SCOPE_ID,'
        ),
        '"isolated_mutation_fields": ["attempt_identity", "record_identity"],': (
            '"isolated_mutation_fields": ["authority_scope"],\n'
            '                    "dependent_recomputation_fields": [\n'
            '                        "canonical_Human_act_content_identity",\n'
            '                        "CHE_source_act_digest",\n'
            '                        "CHE_correlation_identity",\n'
            "                    ],"
        ),
        '"semantic_mutation_field": "attempt_identity",': (
            '"semantic_mutation_field": "authority_scope",'
        ),
    }
    for old, new in replacements.items():
        if old not in transformed:
            raise WrongScopeAdapterError("FC_SCOPE_REDUCTION_ANCHOR_INVALID__" + old)
        transformed = transformed.replace(old, new)

    required = (
        'wrong_act_value["authority_scope"] = WRONG_SCOPE_ID',
        'denial_error == "operational Human act scope is invalid"',
        'authority_differing_fields == ["authority_scope"]',
        '"semantic_mutation_field": "authority_scope"',
        '"authorized_context_sha256": gate.operation_context_sha256',
        '"authorization_reference": ACT_ID',
    )
    if not all(token in transformed for token in required):
        raise WrongScopeAdapterError("FC_WRONG_SCOPE_SPECIALIZATION_INCOMPLETE")
    if 'wrong_value["attempt_identity"] = WRONG_SCOPE_ID' in transformed:
        raise WrongScopeAdapterError("WRONG_ATTEMPT_MUTATION_LEAK")
    compile(transformed, str(source_path), "exec")
    return transformed


def load_guest_runtime_namespace(
    repository_root: Path = GUEST_REPOSITORY_ROOT,
    context_path: Path = GUEST_CONTEXT_PATH,
) -> dict[str, Any]:
    """Authenticate the sealed context and assemble the existing route only."""

    root = repository_root.resolve()
    owner_path = (
        GUEST_PROJECTED_FM_CONTEXT_OWNER
        if root == GUEST_REPOSITORY_ROOT
        else root / FM_CONTEXT_OWNER
    )
    owner = _load(owner_path, "g77_256lg_guest_context_owner")
    context = owner.load_context(context_path, repository_root=root)
    if owner.operation_vector(context["generation_identity"]) != VECTOR:
        raise WrongScopeAdapterError("SEALED_CONTEXT_VECTOR_IS_NOT_WRONG_SCOPE")
    source = specialize_fc_runtime_source(
        repository_root=root,
        identity_namespace_prefix=context["identity_namespace_prefix"],
    )
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_wrong_scope_specialization_v1",
        "__file__": str(root / FC_ADAPTER),
        "__package__": None,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise WrongScopeAdapterError("WRONG_SCOPE_GENERATION_SPECIALIZATION_FAILED")
    namespace["load_er"] = lambda: specialize_er_harness(root)
    return namespace


def main() -> int:
    """Use the existing FC/FM/ER/P11 runtime with the sealed strategy."""

    namespace = load_guest_runtime_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
