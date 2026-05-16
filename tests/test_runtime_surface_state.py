from sapianta_bridge.governed_runtime_surface.runtime_surface_state import RUNTIME_SURFACE_STATES,SUCCESS_PATH
def test_runtime_surface_states_are_bounded():
    assert SUCCESS_PATH[-1]=="RUNTIME_SURFACE_COMPLETED"
    assert RUNTIME_SURFACE_STATES[-2:]==("BLOCKED","FAILED")
