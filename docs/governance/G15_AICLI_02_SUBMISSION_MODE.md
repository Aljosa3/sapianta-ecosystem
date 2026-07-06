# G15-AICLI-02 Submission Mode

## Status

Implemented.

Supersession note: G15-AICLI-03 extends submit mode with a persistent Platform Core conversation session. G15-AICLI-02 remains the stdin capture baseline; G15-AICLI-03 changes session lifetime so submit mode can continue through clarification, approval, cancellation, and runtime completion.

## Problem Observed

Real interactive validation showed that AiCLI short compose sessions work, but large multi-line development prompts pasted into VS Code Terminal can render repeated `aicli compose>` prompts inside or between pasted lines. The prompt flood creates an unusable operator experience for Generation 15-sized requests.

## Root Cause

The interactive compose loop is intentionally line-oriented. It calls `input()` for each input cycle and renders a terminal prompt before each requested line. That model is acceptable for short manual composition, but it is not a stable transport for very large pasted prompts in terminals that deliver pasted content through line-buffered input while also echoing prompts.

The failure is an interface transport problem, not a Platform Core semantic problem. Platform Core already accepts a complete multi-line request when AiCLI submits one complete message.

## Why Line-Oriented Compose Is Not Suitable For Large Pasted Prompts

`input()` is prompt-driven. Large right-click paste flows can interleave terminal echo, prompt rendering, and buffered input delivery in ways that are outside Platform Core control. Continuing to tune line-by-line compose would keep large prompt reliability dependent on terminal paste behavior.

Submission mode avoids that transport class entirely by reading the complete request through `sys.stdin.read()` until EOF, then submitting exactly one complete request to the existing Platform Core project-context path.

## Why Submission Mode Belongs In AiCLI

AiCLI owns only Human Interface capture and presentation. Reading stdin until EOF is an interface capture concern. Platform Core should not know whether the human typed a short request interactively, pasted a large prompt, or piped text from a file.

Submission mode does not add semantic interpretation, governance logic, provider logic, replay ownership, or runtime orchestration to AiCLI.

## Knowledge Reuse Audit

Reused existing AiCLI and Platform Core surfaces:

- `aigol/cli/aicli.py::_submit_composed_request` remains the single local adapter path for submitting a complete request to `prepare_unified_human_interface_project_context`.
- Existing Platform Core project context rendering is reused unchanged.
- Existing Platform Core conversation rendering is reused unchanged for approval summaries, clarification responses, and fail-closed responses.
- Existing workspace-state recording via `record_unified_human_interface_workspace_state` is reused for submit mode session evidence.
- Existing interactive `./aicli` mode remains available and unchanged in behavior.

No duplicate governance, provider, runtime, replay, workspace, knowledge reuse, or conversation semantics were introduced.

## Implementation Summary

Implemented `./aicli submit`.

Submit mode:

- prints `Paste request below.` and `Finish with Ctrl+D.`;
- reads the full request from `sys.stdin.read()`;
- normalizes platform line endings to `\n`;
- strips only surrounding empty input lines;
- preserves internal line breaks and blank lines;
- rejects empty input with a clear message;
- submits non-empty input exactly once through the same Platform Core project-context path used by compose submission;
- records AiCLI session completion while preserving non-authoritative Human Interface flags.

## Boundary Confirmation

AiCLI remains non-authoritative:

- `aicli_authorizes: False`
- `aicli_executes: False`
- `aicli_owns_replay: False`
- `aicli_owns_workspace: False`
- `aicli_owns_goal_mapping: False`
- `aicli_owns_provider_selection: False`

Platform Core remains the owner of semantic interpretation, governance, conversation experience, project context, workspace services, knowledge reuse, and runtime orchestration.

Provider Platform remains unchanged.

## Usage Instructions

Interactive short sessions remain:

```bash
./aicli
```

Large prompt submission:

```bash
./aicli submit
```

AiCLI prints:

```text
Paste request below.
Finish with Ctrl+D.
```

Paste the full development request, then press Ctrl+D. AiCLI submits the collected text to Platform Core exactly once.

## Validation Summary

Focused validation:

```bash
python -m py_compile aigol/cli/aicli.py
python -m pytest tests/test_g15_aicli_02_submission_mode.py -q
python -m pytest -q
git diff --check
```

Result:

```text
5 passed
5812 passed, 4 skipped
```

Regression coverage confirms:

- submit mode accepts a large multi-line prompt;
- submit mode preserves internal line breaks;
- submit mode submits exactly once;
- submit mode rejects empty input without creating a Platform Core project-context submission;
- `main(... submit)` reads stdin;
- existing interactive compose mode still accepts short sessions;
- AiCLI remains non-authoritative.
