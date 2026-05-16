"""Governed runtime surface response."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSurfaceResponse:
    runtime_surface_session_id: str
    surface_egress_id: str
    response_return_id: str
    def to_dict(self) -> dict:
        return {"runtime_surface_session_id": self.runtime_surface_session_id, "surface_egress_id": self.surface_egress_id, "response_return_id": self.response_return_id, "surface_status": "RUNTIME_SURFACE_COMPLETED"}


def create_runtime_surface_response(*, binding: dict) -> RuntimeSurfaceResponse:
    return RuntimeSurfaceResponse(binding["runtime_surface_session_id"], binding["surface_egress_id"], binding["response_return_id"])
