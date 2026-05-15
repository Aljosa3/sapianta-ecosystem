"""Governed live request ingestion request."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LiveRequestIngestionRequest:
    live_request_ingestion_session_id: str
    serving_gateway_session_id: str
    request_activation_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_live_request_ingestion_request(*, ingestion_session: dict) -> LiveRequestIngestionRequest:
    return LiveRequestIngestionRequest(
        ingestion_session["live_request_ingestion_session_id"],
        ingestion_session["serving_gateway_session_id"],
        ingestion_session["request_activation_id"],
    )
