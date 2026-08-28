"""Non-operational future-adapter fixture for the certified EE path grammar.

EE authenticates these declarations from source bytes without importing or
executing this module.  This file is regression input, not a runtime harness,
candidate, authority artifact, or execution entry point.
"""

from pathlib import Path


RAW_ROOT = Path("/mnt/g77-evidence")
CONTINUATION_MANIFEST_PATH = (
    RAW_ROOT / "G77_256EZ_SYNTHETIC_FUTURE_CONTINUATION_MANIFEST_V1.json"
)
