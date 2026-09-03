"""TEST_ONLY projection fixture; it grants no authority and performs no operation."""

from pathlib import Path


FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"
HOST_CANONICAL_IDENTITY = Path("/home/pisarna/work/sapianta-fl")
GUEST_PROJECTED_PATH = Path("/mnt/aigol")
DN_HARNESS_RELATIVE_PATH = Path(
    ".github/governance/evidence/g77_256dn_p03_diagnostic_v1/harness"
)
SEALED_HOST_QEMU_ARGV_SHA256 = (
    "60027a7424727fcc6af40e819fde27df5c4f4d8884ea1f5aedec5a1007062b49"
)
RUNTIME_EXECUTION_IDENTITY = Path("/usr/bin/qemu-system-x86_64")

