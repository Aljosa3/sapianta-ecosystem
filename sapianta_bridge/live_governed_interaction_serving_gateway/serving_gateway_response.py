"""Serving gateway egress response."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServingGatewayResponse:
    serving_gateway_session_id: str
    egress_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "serving_gateway_session_id": self.serving_gateway_session_id,
            "egress_id": self.egress_id,
            "response_return_id": self.response_return_id,
            "serving_status": "SERVING_RESPONSE_EMITTED",
        }


def create_serving_gateway_response(*, gateway_session: dict, binding: dict) -> ServingGatewayResponse:
    return ServingGatewayResponse(gateway_session["serving_gateway_session_id"], gateway_session["egress_id"], binding["response_return_id"])
