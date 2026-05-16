# GOVERNED_RUNTIME_CAPABILITY_MAPPING_V1

This milestone introduces the first governed executable capability realization layer.

It binds each allowed operation type to one deterministic bounded executable primitive. The mapping is static, replay-visible, and fail-closed. No executor is dynamically invented, and forbidden execution surfaces remain rejected.

This advances no-copy/paste work by replacing manual interpretation of how an allowed operation should become executable with explicit governed capability evidence.
