"""Governed provider proposal production runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.provider.certified_provider_attachment import run_certified_provider_attachment
from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
    IMPLEMENTATION_HANDOFF_CREATED,
)
from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import (
    DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
    RESOLUTION_SUCCEEDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    PROVIDER_NECESSITY_CLASSIFIED,
    PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
    PROVIDER_PROHIBITED,
    PROVIDER_REQUIRED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION = "AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_V1"
PROVIDER_REQUEST_PACKET_V1 = "PROVIDER_REQUEST_PACKET_V1"
PROVIDER_REQUEST_PROMPT_PROJECTION_V1 = "PROVIDER_REQUEST_PROMPT_PROJECTION_V1"
PROVIDER_RESPONSE_ARTIFACT_V1 = "PROVIDER_RESPONSE_ARTIFACT_V1"
PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1 = "PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1"
PROVIDER_PROPOSAL_PRODUCED = "PROVIDER_PROPOSAL_PRODUCED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "provider_request_packet_prepared",
    "provider_response_artifact_captured",
    "development_proposal_artifact_produced",
    "provider_proposal_production_returned",
)

FORBIDDEN_AUTHORITY_FIELDS = (
    "authorization_decision",
    "governance_decision",
    "execution_request",
    "dispatch_request",
    "worker_command",
    "provider_command",
    "worker_instruction",
    "memory_mutation",
    "replay_mutation",
    "execution_authority",
    "dispatch_authority",
    "governance_authority",
    "replay_authority",
    "provider_authority",
    "execution_requested",
    "dispatch_requested",
    "worker_created",
    "domain_created",
    "governance_modified",
    "replay_modified",
)


def produce_provider_development_proposal(
    *,
    production_id: str,
    provider_id: str,
    handoff_artifact: dict[str, Any],
    context_assembly_artifact: dict[str, Any],
    registry_resolution_artifact: dict[str, Any],
    provider_necessity_policy_artifact: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Invoke an approved provider as a proposal-only source and validate its proposal."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        handoff = deepcopy(handoff_artifact)
        context = deepcopy(context_assembly_artifact)
        resolution = deepcopy(registry_resolution_artifact)
        policy = deepcopy(provider_necessity_policy_artifact)
        _validate_handoff(handoff)
        _validate_context(context)
        _validate_resolution(resolution)
        _validate_provider_policy(policy)
        _validate_cross_references(handoff=handoff, context=context, resolution=resolution)
        request_packet = _provider_request_packet(
            production_id=production_id,
            provider_id=provider_id,
            handoff=handoff,
            context=context,
            resolution=resolution,
            policy=policy,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_packet)
        prompt_projection = _provider_request_prompt_projection(
            request_packet=request_packet,
            handoff=handoff,
            context=context,
            resolution=resolution,
            created_at=created_at,
        )
        _persist_prompt_projection(replay_path, prompt_projection)
        provider_capture = run_certified_provider_attachment(
            provider_id=provider_id,
            request=prompt_projection,
            proposal_id=f"{production_id}:PROVIDER-ENVELOPE",
            timestamp=created_at,
            registry=registry,
            adapter=adapter,
            replay_dir=replay_path / "provider_attachment",
        )
        response_artifact = _provider_response_artifact(
            production_id=production_id,
            request_packet=request_packet,
            provider_capture=provider_capture,
            created_at=created_at,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response_artifact)
        proposal = _development_proposal_from_response(
            production_id=production_id,
            response_artifact=response_artifact,
            handoff=handoff,
            context=context,
            resolution=resolution,
        )
        validation_capture = validate_development_proposal_contract(
            contract_validation_id=f"{production_id}:PROPOSAL-CONTRACT-VALIDATION",
            proposal_artifact=proposal,
            context_assembly_artifact=context,
            registry_resolution_artifact=resolution,
            created_at=created_at,
            replay_dir=replay_path / "proposal_contract_validation",
        )
        if validation_capture.get("validation_status") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
            raise FailClosedRuntimeError(
                validation_capture.get("failure_reason")
                or "provider proposal production failed closed: proposal contract validation fails"
            )
        produced = _proposal_produced_artifact(
            production_id=production_id,
            request_packet=request_packet,
            response_artifact=response_artifact,
            proposal=proposal,
            validation_capture=validation_capture,
            production_status=PROVIDER_PROPOSAL_PRODUCED,
            created_at=created_at,
            failure_reason=None,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], produced)
        returned = _returned_artifact(produced)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(
            request_packet=request_packet,
            prompt_projection=prompt_projection,
            response_artifact=response_artifact,
            proposal=proposal,
            produced=produced,
            returned=returned,
            replay_path=replay_path,
        )
    except Exception as exc:
        request_packet = locals().get("request_packet")
        response_artifact = locals().get("response_artifact")
        proposal = locals().get("proposal")
        produced = _failed_produced_artifact(
            production_id=production_id,
            provider_id=provider_id,
            handoff=handoff_artifact if isinstance(handoff_artifact, dict) else {},
            context=context_assembly_artifact if isinstance(context_assembly_artifact, dict) else {},
            resolution=registry_resolution_artifact if isinstance(registry_resolution_artifact, dict) else {},
            policy=provider_necessity_policy_artifact
            if isinstance(provider_necessity_policy_artifact, dict)
            else {},
            request_packet=request_packet if isinstance(request_packet, dict) else None,
            response_artifact=response_artifact if isinstance(response_artifact, dict) else None,
            proposal=proposal if isinstance(proposal, dict) else None,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(produced)
        _persist_failure_sequence(replay_path, request_packet, response_artifact, produced, returned)
        return _capture(
            request_packet=request_packet if isinstance(request_packet, dict) else None,
            prompt_projection=prompt_projection if isinstance(locals().get("prompt_projection"), dict) else None,
            response_artifact=response_artifact if isinstance(response_artifact, dict) else None,
            proposal=proposal if isinstance(proposal, dict) else None,
            produced=produced,
            returned=returned,
            replay_path=replay_path,
        )


def reconstruct_provider_proposal_production_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct provider proposal production replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider proposal production replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider proposal production replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "provider proposal production artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    response = wrappers[1]["artifact"]
    produced = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if response.get("provider_request_packet_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal production replay request hash mismatch")
    if produced.get("provider_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal production replay produced request hash mismatch")
    if produced.get("provider_response_hash") != response["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal production replay response hash mismatch")
    if returned.get("production_reference") != produced["production_id"]:
        raise FailClosedRuntimeError("provider proposal production replay reference mismatch")
    if returned.get("production_hash") != produced["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal production replay hash mismatch")
    prompt_projection = None
    prompt_projection_path = replay_path / "000_provider_request_prompt_projection.json"
    if prompt_projection_path.exists():
        prompt_projection_wrapper = load_json(prompt_projection_path)
        if prompt_projection_wrapper.get("replay_step") != "provider_request_prompt_projection":
            raise FailClosedRuntimeError("provider proposal production prompt projection replay step mismatch")
        _verify_wrapper_hash(prompt_projection_wrapper)
        prompt_projection = prompt_projection_wrapper.get("artifact")
        if not isinstance(prompt_projection, dict):
            raise FailClosedRuntimeError("provider proposal production prompt projection must be a JSON object")
        _verify_artifact_hash(prompt_projection, "provider request prompt projection")
        if prompt_projection.get("provider_request_packet_hash") != request["artifact_hash"]:
            raise FailClosedRuntimeError("provider proposal production prompt projection lineage mismatch")
    return {
        "production_id": produced["production_id"],
        "production_status": produced["production_status"],
        "provider_id": produced["provider_id"],
        "provider_invocation_status": produced["provider_invocation_status"],
        "provider_request_hash": produced["provider_request_hash"],
        "provider_response_hash": produced["provider_response_hash"],
        "proposal_hash": produced["proposal_hash"],
        "context_hash": produced["context_hash"],
        "canonical_chain_id": produced["canonical_chain_id"],
        "failure_reason": produced["failure_reason"],
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "provider_request_prompt_projection_present": prompt_projection is not None,
        "provider_request_prompt_projection_hash": prompt_projection.get("artifact_hash")
        if isinstance(prompt_projection, dict)
        else None,
    }


def _validate_handoff(handoff: dict[str, Any]) -> None:
    if handoff.get("artifact_type") != IMPLEMENTATION_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal production failed closed: invalid handoff artifact")
    _verify_artifact_hash(handoff, "implementation handoff")
    if handoff.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
        raise FailClosedRuntimeError("provider proposal production failed closed: handoff is not created")
    if handoff.get("implementation_authorized") is not False:
        raise FailClosedRuntimeError("provider proposal production failed closed: handoff authority violation detected")
    _require_string(handoff.get("handoff_id"), "handoff_id")
    _require_string(handoff.get("task_reference"), "task_reference")
    _require_string(handoff.get("context_reference"), "context_reference")
    _require_string(handoff.get("context_hash"), "context_hash")
    _require_string(handoff.get("domain_reference"), "domain_reference")
    _require_string(handoff.get("worker_reference"), "worker_reference")
    _require_string(handoff.get("milestone_reference"), "milestone_reference")
    _require_nonempty_string_list(handoff.get("output_targets"), "output_targets")
    _assert_no_authority(handoff)


def _validate_context(context: dict[str, Any]) -> None:
    if context.get("artifact_type") != DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal production failed closed: invalid context artifact")
    _verify_artifact_hash(context, "development context assembly")
    if context.get("context_status") != CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("provider proposal production failed closed: context is not assembled")
    _require_string(context.get("context_assembly_id"), "context_assembly_id")
    _require_string(context.get("context_hash"), "context_hash")


def _validate_resolution(resolution: dict[str, Any]) -> None:
    if resolution.get("artifact_type") != DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal production failed closed: invalid registry resolution")
    _verify_artifact_hash(resolution, "domain worker resolution")
    if resolution.get("resolution_status") != RESOLUTION_SUCCEEDED:
        raise FailClosedRuntimeError("provider proposal production failed closed: registry resolution failed")
    _require_string(resolution.get("resolution_id"), "resolution_id")
    _require_string(resolution.get("domain_id"), "domain_id")
    _require_string(resolution.get("worker_family_id"), "worker_family_id")
    _require_string(resolution.get("milestone_type"), "milestone_type")


def _validate_provider_policy(policy: dict[str, Any]) -> None:
    if policy.get("artifact_type") != PROVIDER_NECESSITY_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal production failed closed: invalid provider necessity policy")
    _verify_artifact_hash(policy, "provider necessity policy")
    if policy.get("policy_status") != PROVIDER_NECESSITY_CLASSIFIED:
        raise FailClosedRuntimeError("provider proposal production failed closed: provider necessity not classified")
    classification = policy.get("necessity_classification")
    if classification == PROVIDER_PROHIBITED:
        raise FailClosedRuntimeError("provider proposal production failed closed: provider prohibited by policy")
    if classification != PROVIDER_REQUIRED:
        raise FailClosedRuntimeError("provider proposal production failed closed: provider not required by policy")


def _validate_cross_references(*, handoff: dict[str, Any], context: dict[str, Any], resolution: dict[str, Any]) -> None:
    expected = {
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
    }
    for field, expected_value in expected.items():
        if handoff.get(field) != expected_value:
            raise FailClosedRuntimeError("provider proposal production failed closed: replay mismatch detected")


def _provider_request_packet(
    *,
    production_id: str,
    provider_id: str,
    handoff: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    policy: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
) -> dict[str, Any]:
    packet = {
        "artifact_type": PROVIDER_REQUEST_PACKET_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION,
        "production_id": _require_string(production_id, "production_id"),
        "provider_id": _require_string(provider_id, "provider_id"),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "task_reference": handoff["task_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
        "output_targets": deepcopy(handoff["output_targets"]),
        "constraints": deepcopy(handoff.get("constraints", [])),
        "assumptions": deepcopy(handoff.get("assumptions", [])),
        "known_gaps": deepcopy(handoff.get("known_gaps", [])),
        "provider_necessity_reference": policy["policy_decision_id"],
        "provider_necessity_classification": policy["necessity_classification"],
        "provider_necessity_hash": policy["artifact_hash"],
        "request_instructions": [
            "Return one DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible proposal payload.",
            "Proposal must remain proposal-only.",
            "Do not authorize, dispatch, execute, mutate governance, mutate replay, create workers, or create domains.",
        ],
        "created_at": _require_string(created_at, "created_at"),
        "proposal_only": True,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
    }
    packet["provider_request_hash"] = replay_hash(
        {
            "production_id": packet["production_id"],
            "handoff_hash": packet["handoff_hash"],
            "context_hash": packet["context_hash"],
            "domain_reference": packet["domain_reference"],
            "worker_reference": packet["worker_reference"],
            "milestone_reference": packet["milestone_reference"],
        }
    )
    packet["artifact_hash"] = replay_hash(packet)
    return packet


def _provider_request_prompt_projection(
    *,
    request_packet: dict[str, Any],
    handoff: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    prompt_lines = [
        "Produce one DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible JSON object.",
        "The proposal must remain proposal-only and non-authoritative.",
        "",
        "Task reference: " + _require_string(request_packet.get("task_reference"), "task_reference"),
        "Domain: " + _require_string(request_packet.get("domain_reference"), "domain_reference"),
        "Worker family: " + _require_string(request_packet.get("worker_reference"), "worker_reference"),
        "Milestone: " + _require_string(request_packet.get("milestone_reference"), "milestone_reference"),
        "Output targets: " + ", ".join(_require_nonempty_string_list(request_packet.get("output_targets"), "output_targets")),
        "",
        "Request instructions:",
        *["- " + item for item in _require_nonempty_string_list(request_packet.get("request_instructions"), "request_instructions")],
        "",
        "Constraints:",
        *["- " + item for item in _require_string_list(request_packet.get("constraints", []), "constraints")],
        "",
        "Assumptions:",
        *["- " + item for item in _require_string_list(request_packet.get("assumptions", []), "assumptions")],
        "",
        "Known gaps:",
        *["- " + item for item in _require_string_list(request_packet.get("known_gaps", []), "known_gaps")],
        "",
        "Return JSON with exactly these proposal fields:",
        "- proposal_summary: string, maximum 240 characters",
        "- proposed_outputs: array of strings only; use the output targets exactly as plain strings",
        "- constraints_acknowledged: array of strings",
        "- assumptions: array of strings",
        "- known_gaps: array of strings",
        "",
        "Return only the JSON object. Do not wrap it in Markdown. Do not include nested objects.",
        "",
        "Do not include authorization, execution, dispatch, worker creation, domain creation, governance mutation, or replay mutation fields.",
    ]
    prompt = "\n".join(prompt_lines)
    projection = {
        "artifact_type": PROVIDER_REQUEST_PROMPT_PROJECTION_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION,
        "production_id": request_packet["production_id"],
        "provider_id": request_packet["provider_id"],
        "canonical_chain_id": request_packet["canonical_chain_id"],
        "provider_request_packet_reference": request_packet["production_id"],
        "provider_request_packet_hash": request_packet["artifact_hash"],
        "provider_request_hash": request_packet["provider_request_hash"],
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "registry_resolution_reference": resolution["resolution_id"],
        "registry_resolution_hash": resolution["artifact_hash"],
        "prompt": prompt,
        "human_prompt": prompt,
        "request": prompt,
        "adapter_request_shape": "OPENAI_PROVIDER_PROMPT_REQUEST",
        "proposal_only": True,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    projection["prompt_hash"] = replay_hash(prompt)
    projection["artifact_hash"] = replay_hash(projection)
    return projection


def _provider_response_artifact(
    *,
    production_id: str,
    request_packet: dict[str, Any],
    provider_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    envelope = provider_capture.get("provider_proposal_envelope")
    created = provider_capture.get("provider_proposal_created")
    returned = provider_capture.get("provider_proposal_returned")
    if not isinstance(envelope, dict) or not isinstance(created, dict) or not isinstance(returned, dict):
        raise FailClosedRuntimeError("provider proposal production failed closed: provider response invalid")
    if returned.get("failure_reason"):
        raise FailClosedRuntimeError(returned["failure_reason"])
    response = _normalize_provider_response_payload(envelope.get("response"))
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider proposal production failed closed: provider response invalid")
    _assert_no_authority(response)
    artifact = {
        "artifact_type": PROVIDER_RESPONSE_ARTIFACT_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION,
        "production_id": _require_string(production_id, "production_id"),
        "provider_id": envelope.get("provider_id"),
        "provider_version": envelope.get("provider_version"),
        "provider_request_packet_reference": request_packet["production_id"],
        "provider_request_packet_hash": request_packet["artifact_hash"],
        "provider_attachment_proposal_hash": envelope.get("proposal_hash"),
        "provider_attachment_created_hash": created.get("artifact_hash"),
        "provider_attachment_returned_hash": returned.get("artifact_hash"),
        "provider_response_payload": deepcopy(response),
        "provider_response_payload_hash": replay_hash(response),
        "provider_invocation_status": "PROVIDER_INVOKED",
        "created_at": _require_string(created_at, "created_at"),
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _normalize_provider_response_payload(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider proposal production failed closed: provider response invalid")
    if all(
        field in response
        for field in (
            "proposal_summary",
            "proposed_outputs",
            "constraints_acknowledged",
            "assumptions",
            "known_gaps",
        )
    ):
        return deepcopy(response)
    response_text = response.get("response_text")
    if isinstance(response_text, str) and response_text.strip():
        parsed = _parse_provider_response_text(response_text)
        if isinstance(parsed, dict):
            return parsed
    raise FailClosedRuntimeError("provider proposal production failed closed: provider response invalid")


def _parse_provider_response_text(response_text: str) -> dict[str, Any]:
    stripped = response_text.strip()
    candidates = [stripped]
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            candidates.append("\n".join(lines[1:-1]).strip())
    first_object = _extract_first_json_object(stripped)
    if first_object is not None:
        candidates.append(first_object)
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise FailClosedRuntimeError("provider proposal production failed closed: provider response invalid")


def _extract_first_json_object(value: str) -> str | None:
    start = value.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(value)):
        char = value[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return value[start : index + 1]
    return None


def _development_proposal_from_response(
    *,
    production_id: str,
    response_artifact: dict[str, Any],
    handoff: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
) -> dict[str, Any]:
    response = deepcopy(response_artifact["provider_response_payload"])
    required = (
        "proposal_summary",
        "proposed_outputs",
        "constraints_acknowledged",
        "assumptions",
        "known_gaps",
    )
    for field in required:
        if field not in response:
            raise FailClosedRuntimeError("provider proposal production failed closed: provider response invalid")
    _assert_no_authority(response)
    outputs = _require_nonempty_string_list(response["proposed_outputs"], "proposed_outputs")
    if len(set(outputs)) != len(outputs):
        raise FailClosedRuntimeError("provider proposal production failed closed: ambiguous provider result detected")
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": f"{production_id}:DEVELOPMENT-PROPOSAL",
        "task_reference": handoff["task_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
        "proposal_summary": _require_string(response["proposal_summary"], "proposal_summary"),
        "proposed_outputs": outputs,
        "constraints_acknowledged": _require_string_list(
            response["constraints_acknowledged"], "constraints_acknowledged"
        ),
        "assumptions": _require_string_list(response["assumptions"], "assumptions"),
        "known_gaps": _require_string_list(response["known_gaps"], "known_gaps"),
        "proposal_only": True,
        "provider_response_reference": response_artifact["production_id"],
        "provider_response_hash": response_artifact["artifact_hash"],
        "execution_authority": False,
        "dispatch_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _proposal_produced_artifact(
    *,
    production_id: str,
    request_packet: dict[str, Any],
    response_artifact: dict[str, Any],
    proposal: dict[str, Any],
    validation_capture: dict[str, Any],
    production_status: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION,
        "production_id": _require_string(production_id, "production_id"),
        "production_status": production_status,
        "provider_id": request_packet.get("provider_id"),
        "provider_invocation_status": response_artifact.get("provider_invocation_status"),
        "provider_request_hash": request_packet.get("artifact_hash"),
        "provider_response_hash": response_artifact.get("artifact_hash"),
        "proposal_reference": proposal.get("proposal_id"),
        "proposal_hash": proposal.get("artifact_hash"),
        "context_hash": proposal.get("context_hash"),
        "canonical_chain_id": request_packet.get("canonical_chain_id"),
        "contract_validation_reference": validation_capture.get("contract_validation_id"),
        "contract_validation_hash": validation_capture.get("contract_validation_hash")
        or validation_capture.get("development_proposal_contract_validation_artifact", {}).get("artifact_hash"),
        "validation_status": validation_capture.get("validation_status"),
        "created_at": _require_string(created_at, "created_at"),
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_produced_artifact(
    *,
    production_id: str,
    provider_id: str,
    handoff: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    policy: dict[str, Any],
    request_packet: dict[str, Any] | None,
    response_artifact: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    canonical_chain_id: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    packet = request_packet or {}
    response = response_artifact or {}
    artifact = {
        "artifact_type": PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION,
        "production_id": production_id if isinstance(production_id, str) and production_id.strip() else "INVALID_PRODUCTION_ID",
        "production_status": FAILED_CLOSED,
        "provider_id": provider_id if isinstance(provider_id, str) and provider_id.strip() else "INVALID_PROVIDER_ID",
        "provider_invocation_status": response.get("provider_invocation_status", "PROVIDER_NOT_INVOKED"),
        "provider_request_hash": packet.get("artifact_hash"),
        "provider_response_hash": response.get("artifact_hash"),
        "proposal_reference": proposal.get("proposal_id") if isinstance(proposal, dict) else None,
        "proposal_hash": proposal.get("artifact_hash") if isinstance(proposal, dict) else None,
        "context_hash": context.get("context_hash"),
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "handoff_reference": handoff.get("handoff_id"),
        "registry_resolution_reference": resolution.get("resolution_id"),
        "provider_necessity_reference": policy.get("policy_decision_id"),
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(produced: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(produced, "provider proposal production artifact")
    artifact = {
        "event_type": "PROVIDER_PROPOSAL_PRODUCTION_RETURNED",
        "production_reference": produced["production_id"],
        "production_hash": produced["artifact_hash"],
        "production_status": produced["production_status"],
        "provider_id": produced["provider_id"],
        "provider_invocation_status": produced["provider_invocation_status"],
        "proposal_hash": produced["proposal_hash"],
        "context_hash": produced["context_hash"],
        "canonical_chain_id": produced["canonical_chain_id"],
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": produced["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    request_packet: dict[str, Any] | None,
    prompt_projection: dict[str, Any] | None,
    response_artifact: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    produced: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "provider_request_packet": deepcopy(request_packet),
        "provider_request_prompt_projection": deepcopy(prompt_projection),
        "provider_response_artifact": deepcopy(response_artifact),
        "development_proposal_artifact": deepcopy(proposal),
        "provider_proposal_production_artifact": deepcopy(produced),
        "provider_proposal_production_replay": deepcopy(returned),
        "provider_proposal_production_replay_reference": str(replay_path),
        "production_id": produced["production_id"],
        "production_status": produced["production_status"],
        "provider_id": produced["provider_id"],
        "provider_invocation_status": produced["provider_invocation_status"],
        "provider_request_hash": produced["provider_request_hash"],
        "provider_response_hash": produced["provider_response_hash"],
        "proposal_hash": produced["proposal_hash"],
        "context_hash": produced["context_hash"],
        "canonical_chain_id": produced["canonical_chain_id"],
        "fail_closed": produced["production_status"] == FAILED_CLOSED,
        "failure_reason": produced["failure_reason"],
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["provider_proposal_production_capture_hash"] = replay_hash(capture)
    return capture


def _persist_failure_sequence(
    replay_path: Path,
    request_packet: Any,
    response_artifact: Any,
    produced: dict[str, Any],
    returned: dict[str, Any],
) -> None:
    fallback_request = request_packet if isinstance(request_packet, dict) else _failure_step_artifact("PROVIDER_REQUEST_FAILED")
    fallback_response = (
        response_artifact if isinstance(response_artifact, dict) else _failure_step_artifact("PROVIDER_RESPONSE_FAILED")
    )
    _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], fallback_request)
    _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], fallback_response)
    _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], produced)
    _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)


def _persist_prompt_projection(replay_path: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "provider request prompt projection")
    wrapper = {
        "replay_index": 0,
        "replay_step": "provider_request_prompt_projection",
        "event_type": "PROVIDER_REQUEST_PROMPT_PROJECTION",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / "000_provider_request_prompt_projection.json", wrapper)


def _failure_step_artifact(event_type: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": event_type,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "replay_visible": True,
        "artifact_hash": "",
    }
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider proposal production replay step ordering mismatch")
    _verify_artifact_hash(artifact, "provider proposal production artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("provider proposal production replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider proposal production replay hash mismatch")


def _assert_no_authority(value: Any) -> None:
    if isinstance(value, dict):
        for field in FORBIDDEN_AUTHORITY_FIELDS:
            if value.get(field) is True:
                raise FailClosedRuntimeError("provider proposal production failed closed: authority violation detected")
        for nested in value.values():
            _assert_no_authority(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_no_authority(nested)


def _require_nonempty_string_list(value: Any, field_name: str) -> list[str]:
    items = _require_string_list(value, field_name)
    if not items:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return items


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{field_name} is required")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise FailClosedRuntimeError(f"{field_name} must contain strings")
    return list(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider proposal production failed closed"
