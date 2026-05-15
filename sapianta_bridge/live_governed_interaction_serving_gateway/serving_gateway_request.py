"""Serving gateway ingress request."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServingGatewayRequest:
    serving_gateway_session_id: str
    ingress_id: str
    runtime_serving_session_id: str
    terminal_attachment_session_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_serving_gateway_request(*, gateway_session: dict) -> ServingGatewayRequest:
    return ServingGatewayRequest(
        gateway_session["serving_gateway_session_id"],
        gateway_session["ingress_id"],
        gateway_session["runtime_serving_session_id"],
        gateway_session["terminal_attachment_session_id"],
    )
