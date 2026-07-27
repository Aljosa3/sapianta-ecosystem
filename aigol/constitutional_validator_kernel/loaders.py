"""Authenticated ECC V1, ICEM V1 and immutable evidence loaders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import JsonSource, load_json_object, validate_hash, verify_self_hash
from .errors import ConstitutionalValidationInputError
from .models import EvidenceAuthenticationResult, ValidationStatus, ValidationTrustAnchors
from .rules import validate_rule_schema
from .scheduler import schedule_requirements

VALIDATOR_VERSION = "1.0.0"
CONSTITUTIONAL_VERSION = "V31"
PLATFORM_CORE_VERSION = "V31"

_CONTRACT_ROOT_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_id",
        "schema_version",
        "contract_id",
        "contract_version",
        "constitutional_id",
        "constitutional_version",
        "compatibility_version",
        "title",
        "description",
        "compatibility",
        "deprecation",
        "requirements",
        "contract_hash",
    }
)
_REQUIREMENT_FIELDS = frozenset(
    {
        "requirement_id",
        "title",
        "description",
        "owner",
        "category",
        "verification_class",
        "validation_scope",
        "severity",
        "mandatory",
        "applicability",
        "dependencies",
        "evidence",
        "rule",
        "pass_criteria",
        "fail_criteria",
        "replay_visible",
        "certification_applicability",
        "compatibility",
    }
)
_EVIDENCE_DECLARATION_FIELDS = frozenset(
    {
        "evidence_id",
        "evidence_type",
        "required",
        "artifact_reference",
        "artifact_hash",
        "wrapper_hash",
        "session_binding",
        "chain_binding",
        "lineage_binding",
        "version_binding",
        "immutable_reference",
    }
)
_MANIFEST_ROOT_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_id",
        "schema_version",
        "manifest_id",
        "manifest_version",
        "constitutional_version",
        "contract_binding",
        "validation_context",
        "evidence_order",
        "evidence_records",
        "manifest_hash",
    }
)
_CONTRACT_BINDING_FIELDS = frozenset(
    {
        "contract_reference",
        "contract_id",
        "contract_version",
        "contract_schema_id",
        "contract_schema_version",
        "contract_hash",
    }
)
_VALIDATION_CONTEXT_FIELDS = frozenset(
    {
        "validation_id",
        "validation_scope",
        "invocation_id",
        "session_id",
        "chain_id",
        "platform_core_version",
        "adapter_id",
        "adapter_version",
    }
)
_COMMON_RECORD_FIELDS = frozenset(
    {
        "record_type",
        "evidence_id",
        "evidence_type",
        "evidence_class",
        "constitutional_owner",
        "authority_effect",
        "artifact_reference",
        "artifact_hash",
        "artifact_version",
        "lineage_commitments",
        "replay_binding",
    }
)
_OPTIONAL_RECORD_FIELDS = frozenset(
    {
        "wrapper_reference",
        "wrapper_hash",
        "replay_reference",
        "replay_hash",
    }
)
_LINEAGE_FIELDS = frozenset(
    {
        "lineage_id",
        "artifact_reference",
        "artifact_hash",
        "relationship",
    }
)
_REPLAY_BINDING_FIELDS = frozenset({"mode", "replay_visible", "replay_owner"})
_RECORD_TYPES = frozenset(
    {
        "STATIC_EVIDENCE_RECORD_V1",
        "LIFECYCLE_EVIDENCE_RECORD_V1",
        "CERTIFICATION_EVIDENCE_RECORD_V1",
    }
)
_EVIDENCE_CLASSES = frozenset(
    {
        "PLATFORM_CORE",
        "ADAPTER",
        "WORKER",
        "REPLAY",
        "CERTIFICATION",
    }
)
_AUTHORITY_EFFECTS = frozenset({"NONE", "PLATFORM_CORE_ONLY"})
_LINEAGE_RELATIONSHIPS = frozenset(
    {
        "AUTHENTICATES",
        "DERIVES_FROM",
        "PRECEDES",
        "CONTINUES",
        "PROJECTS_WITHOUT_AUTHORITY",
        "CERTIFIES",
    }
)
_REPLAY_MODES = frozenset(
    {
        "NOT_APPLICABLE",
        "OPTIONAL_REFERENCE",
        "REQUIRED_REFERENCE",
        "DERIVED_REQUIRED_REFERENCE",
    }
)


@dataclass(frozen=True)
class EvidencePolicy:
    evidence_id: str
    evidence_type: str
    wrapper_presence: str
    session_binding: str
    chain_binding: str
    lineage_binding: str
    supported_versions: tuple[str, ...]


@dataclass(frozen=True)
class AuthenticatedContract:
    data: dict[str, Any]
    contract_hash: str
    schedule: tuple[str, ...]
    evidence_policies: tuple[EvidencePolicy, ...]

    @property
    def policy_by_type(self) -> dict[str, EvidencePolicy]:
        return {policy.evidence_type: policy for policy in self.evidence_policies}


@dataclass(frozen=True)
class AuthenticatedEvidenceManifest:
    data: dict[str, Any]
    manifest_hash: str
    evidence_by_contract_id: dict[str, dict[str, Any]]
    evidence_results: tuple[EvidenceAuthenticationResult, ...]


def load_authenticated_contract(
    source: JsonSource,
    trust_anchors: ValidationTrustAnchors,
) -> AuthenticatedContract:
    contract = load_json_object(source, "contract")
    _exact_fields(contract, _CONTRACT_ROOT_FIELDS, "contract")
    _expect_equal(contract["artifact_type"], "EXECUTABLE_CONSTITUTIONAL_CONTRACT_V1", "contract artifact_type")
    _expect_equal(contract["schema_id"], "ECC_V1", "contract schema_id")
    _expect_equal(contract["schema_version"], "1.0.0", "contract schema_version")
    _expect_equal(contract["constitutional_version"], CONSTITUTIONAL_VERSION, "contract constitutional_version")
    _expect_equal(contract["compatibility_version"], "1.0.0", "contract compatibility_version")
    _expect_equal(contract["contract_id"], trust_anchors.contract_id, "contract trust anchor identity")
    _expect_equal(trust_anchors.constitutional_version, CONSTITUTIONAL_VERSION, "trust anchor constitutional version")
    _expect_equal(trust_anchors.platform_core_version, PLATFORM_CORE_VERSION, "trust anchor Platform Core version")
    for field in ("contract_id", "contract_version", "constitutional_id", "title", "description"):
        _require_non_empty_string(contract[field], f"contract.{field}")
    contract_hash = verify_self_hash(contract, "contract_hash", "contract")
    validate_hash(trust_anchors.contract_hash, "trust_anchors.contract_hash")
    _expect_equal(contract_hash, trust_anchors.contract_hash, "contract trust anchor hash")

    compatibility = contract["compatibility"]
    if not isinstance(compatibility, dict):
        _invalid("INVALID_CONTRACT_SCHEMA", "contract.compatibility must be an object")
    _require_supported(compatibility, "supported_schema_versions", contract["schema_version"])
    _require_supported(compatibility, "supported_contract_versions", contract["contract_version"])
    _require_supported(compatibility, "supported_compatibility_versions", contract["compatibility_version"])
    _require_supported(compatibility, "supported_validator_versions", VALIDATOR_VERSION)
    _require_supported(compatibility, "supported_constitutional_versions", CONSTITUTIONAL_VERSION)
    _expect_equal(compatibility.get("unsupported_version_behavior"), "FAIL_CLOSED", "unsupported version behavior")
    _expect_equal(compatibility.get("forward_compatibility"), "EXPLICIT_ONLY", "forward compatibility")
    _expect_equal(compatibility.get("backward_compatibility"), "EXPLICIT_ONLY", "backward compatibility")
    if contract["deprecation"] != {"state": "ACTIVE"}:
        _invalid("DEPRECATED_CONTRACT", "contract must be active")

    requirements = contract["requirements"]
    if not isinstance(requirements, list) or not requirements:
        _invalid("INVALID_CONTRACT_SCHEMA", "contract requirements must be a non-empty array")
    for requirement in requirements:
        _validate_requirement(requirement)
    schedule = schedule_requirements(requirements)
    policies = _collect_evidence_policies(requirements)
    return AuthenticatedContract(
        data=contract,
        contract_hash=contract_hash,
        schedule=schedule,
        evidence_policies=policies,
    )


def load_authenticated_evidence_manifest(
    source: JsonSource,
    *,
    contract: AuthenticatedContract,
    evidence_sources: Mapping[str, JsonSource],
    trust_anchors: ValidationTrustAnchors,
) -> AuthenticatedEvidenceManifest:
    if not isinstance(evidence_sources, Mapping):
        _invalid("INVALID_EVIDENCE_SOURCES", "evidence sources must be an explicit mapping")
    if not all(isinstance(reference, str) for reference in evidence_sources):
        _invalid("INVALID_EVIDENCE_SOURCES", "evidence source references must be strings")

    manifest = load_json_object(source, "evidence manifest")
    _exact_fields(manifest, _MANIFEST_ROOT_FIELDS, "evidence manifest")
    _expect_equal(
        manifest["artifact_type"],
        "IMMUTABLE_CONSTITUTIONAL_EVIDENCE_MANIFEST_V1",
        "manifest artifact_type",
    )
    _expect_equal(manifest["schema_id"], "ICEM_V1", "manifest schema_id")
    _expect_equal(manifest["schema_version"], "1.0.0", "manifest schema_version")
    _expect_equal(manifest["manifest_version"], "1.0.0", "manifest version")
    _expect_equal(manifest["constitutional_version"], CONSTITUTIONAL_VERSION, "manifest constitutional version")
    _expect_equal(manifest["manifest_id"], trust_anchors.manifest_id, "manifest trust anchor identity")
    _require_non_empty_string(manifest["manifest_id"], "manifest.manifest_id")
    manifest_hash = verify_self_hash(manifest, "manifest_hash", "evidence manifest")
    validate_hash(trust_anchors.manifest_hash, "trust_anchors.manifest_hash")
    _expect_equal(manifest_hash, trust_anchors.manifest_hash, "manifest trust anchor hash")

    _validate_contract_binding(manifest["contract_binding"], contract)
    context = _validate_context(manifest["validation_context"], trust_anchors)
    records = manifest["evidence_records"]
    order = manifest["evidence_order"]
    if not isinstance(records, list) or not records:
        _invalid("INVALID_MANIFEST_SCHEMA", "manifest evidence_records must be a non-empty array")
    if not isinstance(order, list) or not order or not all(_is_non_empty_string(item) for item in order):
        _invalid("INVALID_MANIFEST_SCHEMA", "manifest evidence_order must contain identifiers")
    record_ids = [record.get("evidence_id") if isinstance(record, dict) else None for record in records]
    if order != record_ids:
        _invalid("EVIDENCE_ORDER_MISMATCH", "manifest evidence order does not match record order")
    if len(order) != len(set(order)):
        _invalid("DUPLICATE_EVIDENCE", "manifest contains duplicate evidence identifiers")

    policies = contract.policy_by_type
    record_types = [record.get("evidence_type") if isinstance(record, dict) else None for record in records]
    if len(record_types) != len(set(record_types)):
        _invalid("DUPLICATE_EVIDENCE_TYPE", "manifest contains duplicate evidence types")
    if set(record_types) != set(policies):
        _invalid("EVIDENCE_PROFILE_MISMATCH", "manifest evidence types do not exactly cover the contract")

    artifacts_by_reference: dict[str, tuple[str, dict[str, Any]]] = {}
    artifacts_by_contract_id: dict[str, dict[str, Any]] = {}
    authentication_results: list[EvidenceAuthenticationResult] = []
    used_references: set[str] = set()

    for record in records:
        if not isinstance(record, dict):
            _invalid("INVALID_EVIDENCE_RECORD", "manifest evidence record must be an object")
        policy = policies[record["evidence_type"]]
        _validate_record(record, policy, context)
        artifact_reference = record["artifact_reference"]
        artifact = _resolve_json(evidence_sources, artifact_reference, "evidence artifact", used_references)
        artifact_hash = _authenticate_artifact(
            artifact,
            hash_field="artifact_hash",
            expected_hash=record["artifact_hash"],
            label=f"evidence {record['evidence_id']}",
        )
        _expect_equal(artifact.get("artifact_type"), record["evidence_type"], "evidence artifact_type")
        _expect_equal(artifact.get("artifact_version"), record["artifact_version"], "evidence artifact_version")
        artifacts_by_reference[artifact_reference] = (artifact_hash, artifact)
        artifacts_by_contract_id[policy.evidence_id] = artifact
        _authenticate_optional_wrapper(record, artifact_reference, artifact_hash, evidence_sources, used_references)
        _authenticate_replay(record, artifact_reference, artifact_hash, evidence_sources, used_references)
        authentication_results.append(
            EvidenceAuthenticationResult(
                evidence_id=record["evidence_id"],
                evidence_type=record["evidence_type"],
                artifact_reference=artifact_reference,
                artifact_hash=artifact_hash,
                status=ValidationStatus.PASS,
            )
        )

    contract_binding = manifest["contract_binding"]
    evidence_positions = {
        record["artifact_reference"]: index
        for index, record in enumerate(records)
    }
    for index, record in enumerate(records):
        _authenticate_lineage(
            record,
            record_position=index,
            evidence_positions=evidence_positions,
            contract_binding=contract_binding,
            artifacts_by_reference=artifacts_by_reference,
            evidence_sources=evidence_sources,
            used_references=used_references,
        )
    extras = set(evidence_sources) - used_references
    if extras:
        _invalid("EXTRA_EVIDENCE", "evidence sources contain undeclared references")

    return AuthenticatedEvidenceManifest(
        data=manifest,
        manifest_hash=manifest_hash,
        evidence_by_contract_id=artifacts_by_contract_id,
        evidence_results=tuple(authentication_results),
    )


def _validate_requirement(requirement: Any) -> None:
    if not isinstance(requirement, dict):
        _invalid("INVALID_REQUIREMENT_SCHEMA", "contract requirement must be an object")
    _exact_fields(requirement, _REQUIREMENT_FIELDS, "contract requirement")
    requirement_id = _require_non_empty_string(requirement["requirement_id"], "requirement_id")
    for field in (
        "title",
        "description",
        "owner",
        "category",
        "verification_class",
        "validation_scope",
        "severity",
        "certification_applicability",
    ):
        _require_non_empty_string(requirement[field], f"{requirement_id}.{field}")
    if requirement["mandatory"] is not True:
        _invalid("UNSUPPORTED_REQUIREMENT_MODE", f"{requirement_id} must be mandatory")
    if requirement["applicability"] != {"mode": "ALWAYS"}:
        _invalid("UNSUPPORTED_APPLICABILITY", f"{requirement_id} applicability is unsupported")
    dependencies = requirement["dependencies"]
    if not isinstance(dependencies, list) or not all(_is_non_empty_string(item) for item in dependencies):
        _invalid("INVALID_DEPENDENCIES", f"{requirement_id} dependencies are invalid")
    evidence = requirement["evidence"]
    if not isinstance(evidence, list) or not evidence:
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} requires evidence declarations")
    for declaration in evidence:
        _validate_evidence_declaration(requirement_id, declaration)
    validate_rule_schema(requirement["rule"])
    _validate_criteria(requirement_id, requirement["pass_criteria"], "RULE_TRUE")
    _validate_criteria(requirement_id, requirement["fail_criteria"], "RULE_FALSE")
    if requirement["replay_visible"] is not True:
        _invalid("NON_REPLAY_VISIBLE_REQUIREMENT", f"{requirement_id} must remain Replay-visible")
    if not isinstance(requirement["compatibility"], dict):
        _invalid("INVALID_REQUIREMENT_SCHEMA", f"{requirement_id} compatibility must be an object")


def _validate_evidence_declaration(requirement_id: str, declaration: Any) -> None:
    if not isinstance(declaration, dict):
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} evidence declaration must be an object")
    _exact_fields(declaration, _EVIDENCE_DECLARATION_FIELDS, f"{requirement_id} evidence declaration")
    for field in ("evidence_id", "evidence_type"):
        _require_non_empty_string(declaration[field], f"{requirement_id}.{field}")
    if declaration["required"] is not True or declaration["immutable_reference"] is not True:
        _invalid("NON_IMMUTABLE_EVIDENCE", f"{requirement_id} evidence must be required and immutable")
    _expect_equal(declaration["artifact_reference"], "REQUIRED", f"{requirement_id} artifact reference")
    for hash_field in ("artifact_hash", "wrapper_hash"):
        value = declaration[hash_field]
        if not isinstance(value, dict):
            _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id}.{hash_field} must be an object")
        if value.get("algorithm") != "SHA-256" or value.get("format") != "PREFIXED_LOWERCASE_HEX":
            _invalid("UNSUPPORTED_HASH_MODEL", f"{requirement_id}.{hash_field} hash model is unsupported")
        if value.get("presence") not in {"REQUIRED", "OPTIONAL"}:
            _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id}.{hash_field} presence is invalid")
    if declaration["session_binding"] not in {"REQUIRED", "PROHIBITED"}:
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} session binding is unsupported")
    if declaration["chain_binding"] not in {"REQUIRED", "OPTIONAL", "PROHIBITED"}:
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} chain binding is unsupported")
    if declaration["lineage_binding"] not in {"REQUIRED", "OPTIONAL"}:
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} lineage binding is unsupported")
    version = declaration["version_binding"]
    if not isinstance(version, dict) or version.get("presence") != "REQUIRED":
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} version binding is invalid")
    supported = version.get("supported_versions")
    if not isinstance(supported, list) or not supported or not all(_is_non_empty_string(item) for item in supported):
        _invalid("INVALID_EVIDENCE_DECLARATION", f"{requirement_id} supported evidence versions are invalid")


def _collect_evidence_policies(requirements: list[dict[str, Any]]) -> tuple[EvidencePolicy, ...]:
    by_type: dict[str, EvidencePolicy] = {}
    id_to_type: dict[str, str] = {}
    for requirement in requirements:
        for declaration in requirement["evidence"]:
            evidence_id = declaration["evidence_id"]
            evidence_type = declaration["evidence_type"]
            if evidence_id in id_to_type and id_to_type[evidence_id] != evidence_type:
                _invalid("EVIDENCE_ALIAS_CONFLICT", "contract evidence alias maps to multiple evidence types")
            id_to_type[evidence_id] = evidence_type
            candidate = EvidencePolicy(
                evidence_id=evidence_id,
                evidence_type=evidence_type,
                wrapper_presence=declaration["wrapper_hash"]["presence"],
                session_binding=declaration["session_binding"],
                chain_binding=declaration["chain_binding"],
                lineage_binding=declaration["lineage_binding"],
                supported_versions=tuple(declaration["version_binding"]["supported_versions"]),
            )
            existing = by_type.get(evidence_type)
            if existing is not None and existing != candidate:
                _invalid("EVIDENCE_POLICY_CONFLICT", "contract evidence type has conflicting declarations")
            by_type[evidence_type] = candidate
    if len(id_to_type) != len(by_type):
        _invalid("EVIDENCE_TYPE_CONFLICT", "multiple evidence aliases map to the same evidence type")
    return tuple(sorted(by_type.values(), key=lambda item: item.evidence_id))


def _validate_contract_binding(binding: Any, contract: AuthenticatedContract) -> None:
    if not isinstance(binding, dict):
        _invalid("INVALID_CONTRACT_BINDING", "manifest contract binding must be an object")
    _exact_fields(binding, _CONTRACT_BINDING_FIELDS, "manifest contract binding")
    data = contract.data
    expected = {
        "contract_id": data["contract_id"],
        "contract_version": data["contract_version"],
        "contract_schema_id": data["schema_id"],
        "contract_schema_version": data["schema_version"],
        "contract_hash": contract.contract_hash,
    }
    _require_immutable_reference(binding["contract_reference"], "manifest contract reference")
    for field, value in expected.items():
        _expect_equal(binding[field], value, f"manifest contract binding {field}")


def _validate_context(context: Any, trust_anchors: ValidationTrustAnchors) -> dict[str, Any]:
    if not isinstance(context, dict):
        _invalid("INVALID_VALIDATION_CONTEXT", "manifest validation context must be an object")
    _exact_fields(context, _VALIDATION_CONTEXT_FIELDS, "manifest validation context")
    for field in _VALIDATION_CONTEXT_FIELDS:
        _require_non_empty_string(context[field], f"validation_context.{field}")
    _expect_equal(
        context["validation_scope"],
        "COMPLETE_CERTIFIED_FILESYSTEM_ADAPTER_LIFECYCLE",
        "validation scope",
    )
    _expect_equal(context["platform_core_version"], PLATFORM_CORE_VERSION, "validation Platform Core version")
    _expect_equal(context["platform_core_version"], trust_anchors.platform_core_version, "Platform Core trust anchor")
    return context


def _validate_record(record: dict[str, Any], policy: EvidencePolicy, context: Mapping[str, Any]) -> None:
    record_type = record.get("record_type")
    if record_type not in _RECORD_TYPES:
        _invalid("INVALID_EVIDENCE_RECORD", "evidence record type is unsupported")
    conditional = (
        frozenset()
        if record_type == "STATIC_EVIDENCE_RECORD_V1"
        else frozenset({"invocation_id", "session_id", "chain_id"})
        if record_type == "LIFECYCLE_EVIDENCE_RECORD_V1"
        else frozenset({"invocation_id", "session_id", "derived_chain_id"})
    )
    allowed = _COMMON_RECORD_FIELDS | _OPTIONAL_RECORD_FIELDS | conditional
    required = _COMMON_RECORD_FIELDS | conditional
    if not required.issubset(record) or not set(record).issubset(allowed):
        _invalid("INVALID_EVIDENCE_RECORD", f"{record.get('evidence_id', 'evidence')} fields are invalid")
    for field in (
        "evidence_id",
        "evidence_type",
        "evidence_class",
        "constitutional_owner",
        "authority_effect",
        "artifact_version",
    ):
        _require_non_empty_string(record[field], f"evidence record {field}")
    if record["evidence_type"] != policy.evidence_type:
        _invalid("EVIDENCE_TYPE_MISMATCH", "evidence record type does not match contract")
    if record["evidence_class"] not in _EVIDENCE_CLASSES:
        _invalid("INVALID_EVIDENCE_CLASS", "evidence class is unsupported")
    if record["authority_effect"] not in _AUTHORITY_EFFECTS:
        _invalid("AUTHORITY_BOUNDARY_VIOLATION", "evidence authority effect is unsupported")
    if record["evidence_class"] in {"ADAPTER", "WORKER"} and record["authority_effect"] != "NONE":
        _invalid("AUTHORITY_BOUNDARY_VIOLATION", "Adapter and Worker evidence must be non-authoritative")
    if record_type == "CERTIFICATION_EVIDENCE_RECORD_V1" and record["evidence_class"] != "CERTIFICATION":
        _invalid("OWNER_MISMATCH", "certification record must remain owned by Certification")
    _require_immutable_reference(record["artifact_reference"], "evidence artifact reference")
    validate_hash(record["artifact_hash"], "evidence artifact hash")
    if record["artifact_version"] not in policy.supported_versions:
        _invalid("UNSUPPORTED_EVIDENCE_VERSION", "evidence artifact version is unsupported")
    if record_type == "STATIC_EVIDENCE_RECORD_V1":
        if policy.session_binding != "PROHIBITED" or policy.chain_binding != "PROHIBITED":
            _invalid("SESSION_CHAIN_BINDING_MISMATCH", "static evidence conflicts with contract binding policy")
    elif record_type == "LIFECYCLE_EVIDENCE_RECORD_V1":
        _expect_equal(record["invocation_id"], context["invocation_id"], "evidence invocation binding")
        _expect_equal(record["session_id"], context["session_id"], "evidence session binding")
        _expect_equal(record["chain_id"], context["chain_id"], "evidence chain binding")
        if policy.session_binding != "REQUIRED" or policy.chain_binding != "REQUIRED":
            _invalid("SESSION_CHAIN_BINDING_MISMATCH", "lifecycle evidence conflicts with contract binding policy")
    else:
        _expect_equal(record["invocation_id"], context["invocation_id"], "certification invocation binding")
        _expect_equal(record["session_id"], context["session_id"], "certification session binding")
        _expect_equal(record["derived_chain_id"], context["chain_id"], "certification derived chain binding")
        if policy.session_binding != "REQUIRED" or policy.chain_binding != "OPTIONAL":
            _invalid("SESSION_CHAIN_BINDING_MISMATCH", "certification evidence conflicts with contract binding policy")
    _validate_lineage_declarations(record["lineage_commitments"])
    _validate_replay_binding(record)
    _validate_wrapper_presence(record, policy.wrapper_presence)


def _validate_lineage_declarations(commitments: Any) -> None:
    if not isinstance(commitments, list) or not commitments:
        _invalid("INCOMPLETE_LINEAGE", "evidence lineage commitments must be non-empty")
    lineage_ids: list[str] = []
    for commitment in commitments:
        if not isinstance(commitment, dict):
            _invalid("INVALID_LINEAGE", "lineage commitment must be an object")
        _exact_fields(commitment, _LINEAGE_FIELDS, "lineage commitment")
        lineage_ids.append(_require_non_empty_string(commitment["lineage_id"], "lineage_id"))
        _require_immutable_reference(commitment["artifact_reference"], "lineage artifact reference")
        validate_hash(commitment["artifact_hash"], "lineage artifact hash")
        if commitment["relationship"] not in _LINEAGE_RELATIONSHIPS:
            _invalid("INVALID_LINEAGE_RELATIONSHIP", "lineage relationship is unsupported")
    if len(lineage_ids) != len(set(lineage_ids)):
        _invalid("DUPLICATE_LINEAGE", "lineage commitment identifiers must be unique")


def _validate_replay_binding(record: Mapping[str, Any]) -> None:
    binding = record["replay_binding"]
    if not isinstance(binding, dict):
        _invalid("INVALID_REPLAY_BINDING", "replay binding must be an object")
    _exact_fields(binding, _REPLAY_BINDING_FIELDS, "replay binding")
    if binding["mode"] not in _REPLAY_MODES:
        _invalid("INVALID_REPLAY_BINDING", "replay binding mode is unsupported")
    if type(binding["replay_visible"]) is not bool:
        _invalid("INVALID_REPLAY_BINDING", "replay visibility must be Boolean")
    _expect_equal(binding["replay_owner"], "PLATFORM_CORE_REPLAY", "Replay owner")
    has_reference = "replay_reference" in record
    has_hash = "replay_hash" in record
    if has_reference != has_hash:
        _invalid("INCOMPLETE_REPLAY_BINDING", "Replay reference and hash must be atomic")
    if binding["mode"] == "NOT_APPLICABLE" and has_reference:
        _invalid("INVALID_REPLAY_BINDING", "inapplicable Replay binding cannot carry a reference")
    if binding["mode"] in {"REQUIRED_REFERENCE", "DERIVED_REQUIRED_REFERENCE"} and not has_reference:
        _invalid("INCOMPLETE_REPLAY_BINDING", "required Replay reference is missing")
    if has_reference:
        _require_immutable_reference(record["replay_reference"], "Replay reference")
        validate_hash(record["replay_hash"], "Replay hash")


def _validate_wrapper_presence(record: Mapping[str, Any], presence: str) -> None:
    has_reference = "wrapper_reference" in record
    has_hash = "wrapper_hash" in record
    if has_reference != has_hash:
        _invalid("INCOMPLETE_WRAPPER_BINDING", "wrapper reference and hash must be atomic")
    if presence == "REQUIRED" and not has_reference:
        _invalid("INCOMPLETE_WRAPPER_BINDING", "required evidence wrapper is missing")
    if has_reference:
        _require_immutable_reference(record["wrapper_reference"], "wrapper reference")
        validate_hash(record["wrapper_hash"], "wrapper hash")


def _authenticate_optional_wrapper(
    record: Mapping[str, Any],
    artifact_reference: str,
    artifact_hash: str,
    sources: Mapping[str, JsonSource],
    used_references: set[str],
) -> None:
    if "wrapper_reference" not in record:
        return
    wrapper = _resolve_json(sources, record["wrapper_reference"], "evidence wrapper", used_references)
    _authenticate_artifact(
        wrapper,
        hash_field="wrapper_hash",
        expected_hash=record["wrapper_hash"],
        label=f"wrapper {record['evidence_id']}",
    )
    _expect_equal(wrapper.get("artifact_reference"), artifact_reference, "wrapper artifact reference")
    _expect_equal(wrapper.get("artifact_hash"), artifact_hash, "wrapper artifact hash")


def _authenticate_replay(
    record: Mapping[str, Any],
    artifact_reference: str,
    artifact_hash: str,
    sources: Mapping[str, JsonSource],
    used_references: set[str],
) -> None:
    if "replay_reference" not in record:
        return
    replay = _resolve_json(sources, record["replay_reference"], "Replay evidence", used_references)
    _authenticate_artifact(
        replay,
        hash_field="replay_hash",
        expected_hash=record["replay_hash"],
        label=f"Replay {record['evidence_id']}",
    )
    _expect_equal(replay.get("artifact_reference"), artifact_reference, "Replay artifact reference")
    _expect_equal(replay.get("artifact_hash"), artifact_hash, "Replay artifact hash")


def _authenticate_lineage(
    record: Mapping[str, Any],
    *,
    record_position: int,
    evidence_positions: Mapping[str, int],
    contract_binding: Mapping[str, Any],
    artifacts_by_reference: Mapping[str, tuple[str, dict[str, Any]]],
    evidence_sources: Mapping[str, JsonSource],
    used_references: set[str],
) -> None:
    for commitment in record["lineage_commitments"]:
        reference = commitment["artifact_reference"]
        expected_hash = commitment["artifact_hash"]
        if reference == contract_binding["contract_reference"]:
            _expect_equal(expected_hash, contract_binding["contract_hash"], "contract lineage hash")
            continue
        known = artifacts_by_reference.get(reference)
        if known is not None:
            if evidence_positions[reference] >= record_position:
                _invalid(
                    "LINEAGE_ORDER_VIOLATION",
                    "evidence lineage must reference an earlier manifest record",
                )
            _expect_equal(expected_hash, known[0], "evidence lineage hash")
            continue
        lineage = _resolve_json(evidence_sources, reference, "lineage evidence", used_references)
        hash_field = "artifact_hash" if "artifact_hash" in lineage else "lineage_hash"
        _authenticate_artifact(
            lineage,
            hash_field=hash_field,
            expected_hash=expected_hash,
            label=f"lineage {commitment['lineage_id']}",
        )


def _authenticate_artifact(
    artifact: Mapping[str, Any],
    *,
    hash_field: str,
    expected_hash: Any,
    label: str,
) -> str:
    validate_hash(expected_hash, f"{label} expected hash")
    actual = verify_self_hash(artifact, hash_field, label)
    _expect_equal(actual, expected_hash, f"{label} manifest commitment")
    return actual


def _resolve_json(
    sources: Mapping[str, JsonSource],
    reference: str,
    label: str,
    used_references: set[str],
) -> dict[str, Any]:
    if reference not in sources:
        _invalid("MISSING_EVIDENCE", f"{label} reference is not supplied")
    used_references.add(reference)
    return load_json_object(sources[reference], label)


def _validate_criteria(requirement_id: str, value: Any, condition: str) -> None:
    if not isinstance(value, dict) or set(value) != {"condition", "reason_code"}:
        _invalid("INVALID_REQUIREMENT_SCHEMA", f"{requirement_id} criteria are invalid")
    _expect_equal(value["condition"], condition, f"{requirement_id} criteria condition")
    _require_non_empty_string(value["reason_code"], f"{requirement_id} reason code")


def _require_supported(container: Mapping[str, Any], field: str, expected: str) -> None:
    values = container.get(field)
    if not isinstance(values, list) or expected not in values:
        _invalid("UNSUPPORTED_VERSION", f"{field} does not include the required version")


def _exact_fields(value: Mapping[str, Any], fields: frozenset[str], label: str) -> None:
    if set(value) != fields:
        _invalid("CLOSED_SCHEMA_VIOLATION", f"{label} fields do not match the certified closed schema")


def _require_non_empty_string(value: Any, label: str) -> str:
    if not _is_non_empty_string(value):
        _invalid("EMPTY_IDENTIFIER", f"{label} must be a non-empty string")
    return value


def _require_immutable_reference(value: Any, label: str) -> str:
    reference = _require_non_empty_string(value, label)
    if reference.startswith("/") or "\\" in reference or ".." in reference.split("/"):
        _invalid("MUTABLE_OR_UNSAFE_REFERENCE", f"{label} is not an immutable bounded reference")
    return reference


def _expect_equal(actual: Any, expected: Any, label: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        _invalid("AUTHENTICATION_MISMATCH", f"{label} mismatch")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _invalid(code: str, detail: str) -> None:
    raise ConstitutionalValidationInputError(code, detail)


__all__ = [
    "AuthenticatedContract",
    "AuthenticatedEvidenceManifest",
    "EvidencePolicy",
    "load_authenticated_contract",
    "load_authenticated_evidence_manifest",
]
