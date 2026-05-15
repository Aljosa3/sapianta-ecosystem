"""Fail-closed validator for no-copy/paste validation."""

from typing import Any

from .no_copy_paste_validation_binding import validate_binding
from .no_copy_paste_validation_state import SUCCESS_STATE


def validate_flow(*, binding: dict[str, Any], execution: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    errors = list(validate_binding(binding)["errors"])
    capture = execution.get("capture", {})
    if execution.get("bounded_execution_status") not in ("SUCCESS", "RESULT_CAPTURED_WITH_TERMINATION"):
        errors.append({"field": "execution", "reason": "bounded execution did not produce result"})
    if capture.get("bounded_result_captured") is not True:
        errors.append({"field": "result_capture", "reason": "bounded result capture absent"})
    if response.get("status") != SUCCESS_STATE:
        errors.append({"field": "status", "reason": "flow not classified operational"})
    for field in ("manual_prompt_relay_present", "continuity_fabricated", "provider_success_fabricated"):
        if response.get(field) is not False:
            errors.append({"field": field, "reason": "forbidden proof mutation"})
    return {"valid": not errors, "errors": errors}
