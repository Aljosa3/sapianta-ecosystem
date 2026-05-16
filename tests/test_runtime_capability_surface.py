from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_surface import (
    create_runtime_capability_surface,
)


def test_surface_forbids_unbounded_execution():
    surface = create_runtime_capability_surface(runtime_capability_mapping_id="MAP-1")
    assert surface["raw_shell_execution_allowed"] is False
    assert surface["unrestricted_subprocess_allowed"] is False
    assert surface["unrestricted_network_execution_allowed"] is False
