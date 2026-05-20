# CHATGPT_SEMANTIC_PROPOSAL_IMPORT_V1_ACCEPTANCE

## Acceptance Status

Accepted for finalization.

## Accepted Capabilities

- explicit local semantic proposal import
- human-mediated paste/import bridge
- deterministic local proposal validation
- required proposal field validation
- bounded mode admission for `READ_ONLY`, `REVIEW_ONLY`, and `DEMO_ONLY`
- unsafe mode rejection
- semantic proposal artifact inspection
- accepted proposal continuity cockpit rendering
- rejected proposal blocked rendering

## Acceptance Evidence

The Browser Companion sidepanel now accepts operator-pasted semantic proposal
JSON and validates it locally before rendering any governed continuity cockpit
output.

The bridge preserves the constitutional separation:

- ChatGPT / LLMs provide semantic cognition.
- AiGOL / AGOL governs admissible semantic direction and continuity visibility.
- Codex / providers remain outside this import path and receive no dispatch.

## Governance Acceptance

- ChatGPT API integration: absent
- provider calls: absent
- backend routes: absent
- dispatch: absent
- approval: absent
- execution: absent
- durable persistence: absent
- replay mutation: absent
- lifecycle mutation: absent
- orchestration runtime: absent
- autonomous continuation: absent
- hidden authority: absent

## Test Evidence

Focused validation:

`python -B -m pytest tests/test_chatgpt_semantic_proposal_import.py`

Full repository validation:

`python -B -m pytest tests`

Whitespace validation:

`git diff --check`
