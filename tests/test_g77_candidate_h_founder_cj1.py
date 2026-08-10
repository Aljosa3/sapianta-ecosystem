from __future__ import annotations

import math

import pytest

from aigol.constitutional_validator_kernel.canonical import canonical_json
from aigol.runtime.candidate_h_founder.cj1 import (
    CJ1Error,
    cj1_decode,
    cj1_digest,
    cj1_encode,
    cj1_identity,
)
from aigol.runtime.transport.serialization import canonical_serialize


GOLDEN_VALUE = {"é": [True, False, 0, -7], "a": None}
GOLDEN_BYTES = b'{"a":null,"\xc3\xa9":[true,false,0,-7]}'
GOLDEN_SHA256 = "ee73c562e399e55bbdf85c4a5eeca82a2d376e357711dec88d5219b66b33808d"


def test_exact_golden_bytes_and_repeated_determinism() -> None:
    assert cj1_encode(GOLDEN_VALUE) == GOLDEN_BYTES
    assert cj1_encode({"a": None, "é": [True, False, 0, -7]}) == GOLDEN_BYTES
    assert {cj1_encode(GOLDEN_VALUE) for _ in range(20)} == {GOLDEN_BYTES}
    assert cj1_decode(GOLDEN_BYTES) == {"a": None, "é": [True, False, 0, -7]}


def test_unicode_key_order_and_minimal_escaping() -> None:
    value = {"z": "quote\" slash/ backslash\\ line\n", "é": "é", "a": "x"}
    assert cj1_encode(value) == (
        b'{"a":"x","z":"quote\\\" slash/ backslash\\\\ line\\n",'
        b'"\xc3\xa9":"\xc3\xa9"}'
    )
    with pytest.raises(CJ1Error, match="not NFC"):
        cj1_encode({"value": "e\u0301"})
    with pytest.raises(CJ1Error, match="not NFC"):
        cj1_encode({"e\u0301": "value"})


@pytest.mark.parametrize(
    "value",
    [1.0, math.nan, math.inf, -math.inf, {1: "non-string-key"}, {"x": {1, 2}}],
)
def test_unsupported_values_fail_closed(value: object) -> None:
    with pytest.raises(CJ1Error):
        cj1_encode(value)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a": null}',
        b'{"b":1,"a":2}',
        b'{"a":1,"a":1}',
        b'{"a":-0}',
        b'{"a":01}',
        b'{"a":1.0}',
        b'{"a":NaN}',
        b'{"\\u00e9":1}',
        b'\xef\xbb\xbf{}',
        b'"\xff"',
    ],
)
def test_noncanonical_or_invalid_bytes_fail_closed(raw: bytes) -> None:
    with pytest.raises(CJ1Error):
        cj1_decode(raw)


def test_digest_determinism_and_domain_separation() -> None:
    assert cj1_digest(GOLDEN_VALUE) == f"sha256:{GOLDEN_SHA256}"
    assert cj1_identity("domain-v1", GOLDEN_VALUE) == f"domain-v1:{GOLDEN_SHA256}"
    assert cj1_identity("domain-v2", GOLDEN_VALUE) == f"domain-v2:{GOLDEN_SHA256}"
    assert cj1_identity("domain-v1", GOLDEN_VALUE) != cj1_identity("domain-v2", GOLDEN_VALUE)
    with pytest.raises(CJ1Error):
        cj1_identity("bad:domain", GOLDEN_VALUE)


def test_candidate_codec_is_not_a_generic_serializer_alias() -> None:
    assert canonical_serialize({"é": None}) != cj1_encode({"é": None})
    with pytest.raises(Exception):
        canonical_json({"nullable": None})
    assert cj1_encode({"nullable": None}) == b'{"nullable":null}'
