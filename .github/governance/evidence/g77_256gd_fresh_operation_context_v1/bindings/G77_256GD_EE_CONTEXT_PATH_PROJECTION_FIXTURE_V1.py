#!/usr/bin/env python3
"""TEST_ONLY / NON_AUTHORITY / NON_OPERATIONAL EE path projection.

This file is not a harness and has no executable entry point.  It projects the
two static declarations consumed by the unchanged EE validator from the sealed
G77_256GDVALID01 context fixture.  DU separately authenticates the actual FM
wrapper bytes through the regenerated candidate binding.
"""

from pathlib import Path


FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"
RAW_ROOT = Path("/mnt/g77-evidence")
CONTINUATION_MANIFEST_PATH = (
    RAW_ROOT / "G77_256GDVALID01_CONTINUATION_MANIFEST_V1.json"
)
