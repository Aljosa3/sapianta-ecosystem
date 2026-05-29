# Important Gaps V1

Status: usefulness improvements that should not block first operation.

## Important Gap 1: Result Formatting Stability

Governed result summaries should become stable enough for humans and tests to read consistently.

Useful additions:

- stable status fields
- concise result title
- capability label
- replay verification status
- failure reason summary

## Important Gap 2: Capability Selection Clarity

The operator flow currently requires explicit capability targeting. A first useful AiGOL may benefit from a small deterministic selector that maps a narrow prompt class to one of the two frozen read-only capabilities.

Constraint:

This must be deterministic and rule-based. It must not become autonomous routing or semantic planning.

## Important Gap 3: Replay Storage Convention

Replay evidence should have a clear convention for where operator runs are stored.

Useful additions:

- one default local replay directory
- one run identifier convention
- documented cleanup policy
- clear separation between runtime evidence and source-controlled governance files

## Important Gap 4: Operator Error Taxonomy

Rejected flows should map failure reasons into a small taxonomy.

Possible categories:

- malformed prompt
- unsupported capability
- unauthorized request
- filesystem boundary violation
- replay discontinuity
- hidden continuation attempt

## Important Gap 5: Regression Suite Grouping

Existing tests are useful, but first useful operation benefits from a single named test target for the frozen epoch.

Useful additions:

- one focused test command
- no broad unrelated test execution
- explicit coverage of accepted and rejected paths

## Important Gap 6: Terminology Compression

Future artifacts should prefer fewer terms:

- proposal
- governance
- authorization
- worker execution
- replay
- governed result

This reduces semantic drift.
