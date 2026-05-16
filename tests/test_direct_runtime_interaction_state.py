from sapianta_bridge.governed_direct_runtime_interaction.direct_runtime_interaction_state import DIRECT_RUNTIME_INTERACTION_STATES,SUCCESS_PATH
def test_states_bounded():
    assert SUCCESS_PATH[-1]=="DIRECT_RUNTIME_INTERACTION_RETURNED"; assert DIRECT_RUNTIME_INTERACTION_STATES[-2:]==("BLOCKED","FAILED")
