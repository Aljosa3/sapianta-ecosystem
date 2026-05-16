"""Governed runtime execution commit response envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeExecutionCommitResponse:
    runtime_execution_commit_id: str
    result_capture_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "runtime_execution_commit_id": self.runtime_execution_commit_id,
            "result_capture_id": self.result_capture_id,
            "response_return_id": self.response_return_id,
            "commit_status": "RUNTIME_EXECUTION_COMMIT_FINALIZED",
        }


def create_runtime_execution_commit_response(*, binding: dict) -> RuntimeExecutionCommitResponse:
    return RuntimeExecutionCommitResponse(binding["runtime_execution_commit_id"], binding["result_capture_id"], binding["response_return_id"])
