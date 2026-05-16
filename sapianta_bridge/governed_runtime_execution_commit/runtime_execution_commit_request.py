"""Governed runtime execution commit request envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeExecutionCommitRequest:
    runtime_execution_commit_id: str
    runtime_activation_gate_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_runtime_execution_commit_request(*, commit_session: dict) -> RuntimeExecutionCommitRequest:
    return RuntimeExecutionCommitRequest(commit_session["runtime_execution_commit_id"], commit_session["runtime_activation_gate_id"])
