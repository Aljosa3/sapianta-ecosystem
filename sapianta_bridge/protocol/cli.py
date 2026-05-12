"""Command-line protocol validation entrypoint."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .enforcement import cli_validation_output, enforce_artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if len(args) != 2 or args[0] != "validate":
        print(
            json.dumps(
                {
                    "valid": False,
                    "artifact_type": "unknown",
                    "errors": [
                        {
                            "field": "command",
                            "reason": "usage: python -m sapianta_bridge.protocol.cli validate path/to/artifact.json",
                        }
                    ],
                    "recommended_state": "QUARANTINED",
                },
                sort_keys=True,
            )
        )
        return 2

    try:
        result = enforce_artifact_path(Path(args[1]))
        output = cli_validation_output(result)
        print(json.dumps(output, sort_keys=True))
        return 0 if result.allowed_to_continue else 1
    except Exception as exc:  # pragma: no cover - defensive fail-closed guard.
        print(
            json.dumps(
                {
                    "valid": False,
                    "artifact_type": "unknown",
                    "errors": [
                        {
                            "field": "internal_validator",
                            "reason": f"internal validator failure: {exc.__class__.__name__}",
                        }
                    ],
                    "recommended_state": "QUARANTINED",
                },
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

