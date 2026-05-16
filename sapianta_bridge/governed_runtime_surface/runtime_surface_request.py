"""Governed runtime surface request."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSurfaceRequest:
    runtime_surface_session_id: str
    surface_ingress_id: str
    runtime_delivery_finalization_id: str
    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_runtime_surface_request(*, surface_session: dict) -> RuntimeSurfaceRequest:
    return RuntimeSurfaceRequest(surface_session["runtime_surface_session_id"], surface_session["surface_ingress_id"], surface_session["runtime_delivery_finalization_id"])
