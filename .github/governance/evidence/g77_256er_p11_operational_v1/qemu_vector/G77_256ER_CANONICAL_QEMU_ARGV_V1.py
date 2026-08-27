#!/usr/bin/env python3
"""Single canonical QEMU argv binding shared by producer, verifier, and boot gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from typing import Sequence


DOMAIN = b"SAPIANTA_G77_256ER_CANONICAL_QEMU_ARGV_V1\x00"
U64 = struct.Struct(">Q")


class ArgvBindingError(ValueError):
    """Fail-closed canonical argv error."""


def canonical_argv_bytes(argv: Sequence[str]) -> bytes:
    """Encode exact argv as domain || argc || repeated byte-length || UTF-8 bytes.

    argv[0] participates. Order, empty strings, whitespace, relative/absolute path
    spelling, host-only paths, and literal environment-variable text are preserved.
    No normalization, environment expansion, shell parsing, or fallback encoding is
    permitted. NUL is rejected because POSIX process argv cannot represent it.
    """
    if isinstance(argv, (str, bytes)) or not isinstance(argv, Sequence):
        raise ArgvBindingError("argv must be a sequence of strings")
    encoded: list[bytes] = []
    for index, argument in enumerate(argv):
        if not isinstance(argument, str):
            raise ArgvBindingError(f"argv[{index}] is not a string")
        if "\x00" in argument:
            raise ArgvBindingError(f"argv[{index}] contains NUL")
        try:
            encoded.append(argument.encode("utf-8", errors="strict"))
        except UnicodeEncodeError as exc:
            raise ArgvBindingError(f"argv[{index}] is not strict UTF-8 encodable") from exc
    return DOMAIN + U64.pack(len(encoded)) + b"".join(
        U64.pack(len(argument)) + argument for argument in encoded
    )


def argv_sha256(argv: Sequence[str]) -> str:
    return hashlib.sha256(canonical_argv_bytes(argv)).hexdigest()


def verify_argv(argv: Sequence[str], expected_sha256: str) -> bool:
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ArgvBindingError("expected digest is not lowercase SHA-256")
    if any(character not in "0123456789abcdef" for character in expected_sha256):
        raise ArgvBindingError("expected digest is not lowercase SHA-256")
    return argv_sha256(argv) == expected_sha256


def validation_matrix() -> dict[str, object]:
    baseline = [
        "/usr/bin/qemu-system-x86_64", "-nic", "none", "-drive",
        "file=/tmp/g77_256er/guest-overlay.qcow2,if=virtio,format=qcow2",
        "-drive", "file=/tmp/g77_256er/nocloud-seed.img,if=virtio,format=raw,readonly=on",
    ]
    mutations = {
        "order": [baseline[1], baseline[0], *baseline[2:]],
        "insertion": [*baseline, "-no-reboot"],
        "deletion": baseline[:-1],
        "empty_argument": [*baseline, ""],
        "whitespace": [*baseline[:-1], baseline[-1] + " "],
        "executable_identity": ["qemu-system-x86_64", *baseline[1:]],
        "path": [*baseline[:-3], baseline[-3].replace("g77_256er", "g77_256er_alt"), *baseline[-2:]],
        "image_argument": [*baseline[:-3], baseline[-3].replace("guest-overlay", "other-overlay"), *baseline[-2:]],
        "seed_argument": [*baseline[:-1], baseline[-1].replace("nocloud-seed", "other-seed")],
        "network_argument": [baseline[0], "-nic", "user", *baseline[3:]],
        "duplicate_argument": [*baseline, "-nic", "none"],
    }
    digest = argv_sha256(baseline)
    results = {name: argv_sha256(vector) != digest for name, vector in mutations.items()}
    results.update({
        "token_boundary_ab_c_vs_a_bc": argv_sha256(["ab", "c"]) != argv_sha256(["a", "bc"]),
        "empty_vs_absent": argv_sha256([""]) != argv_sha256([]),
        "framing_domain_change": hashlib.sha256(canonical_argv_bytes(baseline)).digest()
        != hashlib.sha256(canonical_argv_bytes(baseline)[1:]).digest(),
    })
    return {
        "schema_id": "G77_256ER_CANONICAL_QEMU_ARGV_VALIDATION_MATRIX_V1",
        "algorithm": "SHA256_DOMAIN_U64BE_ARGC_REPEATED_U64BE_UTF8_BYTE_LENGTH_AND_BYTES",
        "argv0_included": True,
        "normalization_allowed": False,
        "environment_expansion_allowed": False,
        "baseline_sha256": digest,
        "negative_results": results,
        "result": "PASS" if all(results.values()) else "FAIL",
    }


def load_vector(path: Path) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ArgvBindingError("vector JSON must be an array")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--digest-json", type=Path)
    mode.add_argument("--verify-json", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    if args.self_test:
        result = validation_matrix()
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0 if result["result"] == "PASS" else 1
    vector_path = args.digest_json or args.verify_json
    assert vector_path is not None
    vector = load_vector(vector_path)
    if args.digest_json:
        if args.expected_sha256 is not None:
            parser.error("--digest-json accepts no expected digest")
        print(argv_sha256(vector))
        return 0
    if args.expected_sha256 is None:
        parser.error("--verify-json requires --expected-sha256")
    result = verify_argv(vector, args.expected_sha256)
    print("PASS" if result else "FAIL")
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
