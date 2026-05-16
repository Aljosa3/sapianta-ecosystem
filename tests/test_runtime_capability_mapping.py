from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_mapping import (
    ALLOWED_CAPABILITY_MAPPINGS,
    create_runtime_capability_mapping_record,
)


def test_allowed_mappings_are_deterministic():
    for operation_type, executor in ALLOWED_CAPABILITY_MAPPINGS.items():
        mapping = create_runtime_capability_mapping_record(
            operation_evidence={"runtime_operation_envelope_id": "ENV-1", "operation_type": operation_type}
        )
        assert mapping["executor_primitive"] == executor
