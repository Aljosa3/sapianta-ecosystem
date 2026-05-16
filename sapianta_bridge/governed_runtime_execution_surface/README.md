# Governed Runtime Execution Surface V1

This package realizes bounded executor primitives as deterministic executable runtime surfaces.

Capability mappings state which executor primitive is allowed. Execution surfaces state which exact bounded runtime surface may realize that primitive. The mapping is static, replay-visible, and fail-closed; no execution is performed here.
