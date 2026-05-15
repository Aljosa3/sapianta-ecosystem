# Governed Terminal Runtime Attachment V1

This package attaches the existing governed runtime serving layer to a bounded terminal surface through explicit replay-visible `stdin` and `stdout` continuity bindings.

It preserves terminal attachment identity, runtime serving identity, governed execution lineage, and response continuity without creating a free-form shell, hidden provider memory, or autonomous continuation path.

The attachment is deterministic and fail-closed. Missing serving lineage, missing terminal bindings, identity drift, or incomplete runtime linkage blocks emission.
