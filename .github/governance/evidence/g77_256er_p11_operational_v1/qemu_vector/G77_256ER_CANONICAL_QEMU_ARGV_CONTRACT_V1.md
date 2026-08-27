# G77-256ER Canonical QEMU Argument Vector Contract V1

Status: bounded repository-only pre-boot binding contract.

The single canonical preimage is:

```text
DOMAIN = UTF8("SAPIANTA_G77_256ER_CANONICAL_QEMU_ARGV_V1") || 0x00
PREIMAGE = DOMAIN || U64BE(ARGC) || FOR_EACH_ARG_IN_EXACT_ORDER(U64BE(LEN(UTF8(ARG))) || UTF8(ARG))
DIGEST = SHA256(PREIMAGE)
```

Normative rules:

- the object is the exact ordered process argument vector;
- `argv[0]` is included;
- every item is a string encoded with strict UTF-8;
- argument count and every UTF-8 byte length are unsigned 64-bit big-endian integers;
- argument order and duplicates are preserved;
- `[]` and `[""]` differ;
- no separator characters or trailing newline participate beyond the declared binary framing;
- no shell representation, JSON representation, display string, or semantic-argument subset is accepted;
- no executable or path normalization is allowed;
- absolute and relative path spelling remains exact;
- host-only transient paths participate exactly as passed;
- environment variables are neither read nor expanded; literal `$` text remains literal;
- NUL is rejected because the process argv interface cannot represent it; and
- producer, independent verifier, and boot gate use the same implementation at `qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py`.

No fallback digest, historical EP exception, or alternate dialect is permitted.
