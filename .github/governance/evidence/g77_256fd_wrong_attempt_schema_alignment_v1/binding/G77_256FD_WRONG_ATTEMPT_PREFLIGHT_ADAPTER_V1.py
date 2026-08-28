"""Static EE path binding for the repository-only FD preflight candidate."""

from pathlib import Path


FC_OPERATIONAL_ADAPTER_PATH = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_OPERATIONAL_ADAPTER_SHA256 = "ef564f54fc764ed3968d94365a56a09f06025ea1f534c4a08f818183ddef2e8d"
RAW_ROOT = Path("/mnt/g77-evidence")
CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256FD_CONTINUATION_MANIFEST_V1.json"
REPOSITORY_PREFLIGHT_ONLY = True
OPERATIONAL_AUTHORITY = False
