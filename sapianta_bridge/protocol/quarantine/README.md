# Protocol Quarantine

This directory stores append-only quarantine records for malformed or governance-unsafe protocol artifacts.

Quarantine is isolation, not repair. Artifacts are preserved exactly as received, alongside a deterministic evidence envelope containing the reason, validation errors, source path, timestamp, and source hash.

Categories:

- `malformed/`
- `invalid_hash/`
- `invalid_lineage/`
- `invalid_lifecycle/`
- `unknown_artifact/`

Quarantined artifacts must not be silently modified, deleted, repaired, reclassified, or allowed to continue. Future runtime layers must treat quarantine as a blocking governance state.

