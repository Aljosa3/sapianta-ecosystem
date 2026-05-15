"""Governed live request ingestion response."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LiveRequestIngestionResponse:
    live_request_ingestion_session_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "live_request_ingestion_session_id": self.live_request_ingestion_session_id,
            "response_return_id": self.response_return_id,
            "ingestion_status": "LIVE_RESPONSE_CONTINUITY_READY",
        }


def create_live_request_ingestion_response(*, binding: dict) -> LiveRequestIngestionResponse:
    return LiveRequestIngestionResponse(binding["live_request_ingestion_session_id"], binding["response_return_id"])
