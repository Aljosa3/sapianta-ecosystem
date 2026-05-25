"""Bounded governed capability executor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .capability_request import CapabilityRequest
from .capability_result import CapabilityResult, capability_result_boundary_guarantees
from .capability_validator import CapabilityValidator


class CapabilityExecutor:
    """Executes only bounded sandbox-authorized capabilities."""

    def __init__(self, validator: CapabilityValidator | None = None) -> None:
        self.validator = validator or CapabilityValidator()

    def execute(self, request: CapabilityRequest, sandbox_context) -> CapabilityResult:
        self.validator.validate(request, sandbox_context)
        if request.capability == "read_text":
            summary = self._read_text(request)
        elif request.capability == "inspect_json":
            summary = self._inspect_json(request)
        elif request.capability == "analyze_text":
            summary = self._analyze_text(request)
        elif request.capability == "mock_write_preview":
            summary = self._mock_write_preview(request)
        else:
            raise FailClosedRuntimeError("capability is not executable")
        result = CapabilityResult(
            capability_request_id=request.capability_request_id,
            runtime_id=request.runtime_id,
            sandbox_id=request.sandbox_id,
            capability=request.capability,
            execution_status="CAPABILITY_EXECUTION_COMPLETED",
            execution_summary=summary,
            boundary_guarantees=capability_result_boundary_guarantees(),
            execution_timestamp=request.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        return CapabilityResult(
            capability_request_id=result.capability_request_id,
            runtime_id=result.runtime_id,
            sandbox_id=result.sandbox_id,
            capability=result.capability,
            execution_status=result.execution_status,
            execution_summary=result.execution_summary,
            boundary_guarantees=result.boundary_guarantees,
            execution_timestamp=result.execution_timestamp,
            replay_hash=replay_hash(replay_input),
        )

    def _read_text(self, request: CapabilityRequest) -> dict[str, Any]:
        safe_paths = request.request_payload.get("safe_paths") if isinstance(request.request_payload, dict) else None
        if not isinstance(safe_paths, list) or not safe_paths:
            raise FailClosedRuntimeError("read_text requires explicit safe_paths")
        target = Path(request.target).resolve()
        safe_roots = [Path(path).resolve() for path in safe_paths]
        if not any(target == root or root in target.parents for root in safe_roots):
            raise FailClosedRuntimeError("read_text target is outside approved safe paths")
        if not target.is_file():
            raise FailClosedRuntimeError("read_text target must be an existing file")
        text = target.read_text(encoding="utf-8")
        return {
            "operation": "read_text",
            "target": str(target),
            "text": text,
            "character_count": len(text),
            "read_only": True,
        }

    def _inspect_json(self, request: CapabilityRequest) -> dict[str, Any]:
        payload = request.request_payload.get("json") if isinstance(request.request_payload, dict) else request.request_payload
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, (dict, list)):
            raise FailClosedRuntimeError("inspect_json requires JSON object or array")
        return {
            "operation": "inspect_json",
            "json_type": type(payload).__name__,
            "top_level_count": len(payload),
            "keys": sorted(payload) if isinstance(payload, dict) else [],
        }

    def _analyze_text(self, request: CapabilityRequest) -> dict[str, Any]:
        text = request.request_payload.get("text") if isinstance(request.request_payload, dict) else request.request_payload
        if not isinstance(text, str):
            raise FailClosedRuntimeError("analyze_text requires text")
        words = [word for word in text.split() if word]
        return {
            "operation": "analyze_text",
            "character_count": len(text),
            "word_count": len(words),
            "line_count": len(text.splitlines()) if text else 0,
        }

    def _mock_write_preview(self, request: CapabilityRequest) -> dict[str, Any]:
        content = request.request_payload.get("content", "") if isinstance(request.request_payload, dict) else ""
        if not isinstance(content, str):
            raise FailClosedRuntimeError("mock_write_preview content must be text")
        return {
            "operation": "mock_write_preview",
            "target": request.target,
            "preview_content": content,
            "filesystem_mutation": False,
        }
