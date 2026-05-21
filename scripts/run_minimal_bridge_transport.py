#!/usr/bin/env python3
"""Run the explicit minimal governed bridge transport path."""

from __future__ import annotations

import argparse
import json

from agol_bridge.runtime.minimal_explicit_transport_path import run_minimal_explicit_governed_transport_path_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Run explicit governed request artifact through minimal bridge.")
    parser.add_argument("input_path", help="Path to ChatGPT-prepared governed request JSON artifact.")
    parser.add_argument("output_path", help="Path to write canonical bridge_result_artifact.json.")
    args = parser.parse_args()

    report = run_minimal_explicit_governed_transport_path_file(
        input_path=args.input_path,
        output_path=args.output_path,
    )
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "TRANSPORT_PATH_EXPORTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
