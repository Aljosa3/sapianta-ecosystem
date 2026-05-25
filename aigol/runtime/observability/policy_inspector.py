"""Read-only policy inspection."""

from __future__ import annotations

from aigol.runtime.transport.runtime_store import RuntimeStore


class PolicyInspector:
    def __init__(self, store: RuntimeStore) -> None:
        self.store = store

    def inspect(self, runtime_id: str) -> dict:
        contract = self.store.load_policy_contract(runtime_id)
        validation = self.store.load_policy_validation(runtime_id)
        result = self.store.load_policy_result(runtime_id)
        return {
            "status": "POLICY_INSPECTED",
            "runtime_id": runtime_id,
            "policy_contract": contract,
            "policy_validation": validation,
            "policy_result": result,
            "policy_scope": contract.get("policy_scope"),
            "decision": result.get("decision"),
            "denied_capabilities": result.get("denied_capabilities", []),
        }
