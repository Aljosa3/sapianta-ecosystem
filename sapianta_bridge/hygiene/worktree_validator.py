"""Deterministic governance worktree hygiene validator."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .hygiene_rules import validate_gitignore_text
from .replay_pollution_guard import detect_replay_pollution


def validate_candidate_paths(paths: list[str], *, gitignore_text: str | None = None) -> dict[str, Any]:
    pollution = detect_replay_pollution(paths)
    gitignore = (
        {"valid": True, "missing_patterns": [], "required_patterns": []}
        if gitignore_text is None
        else validate_gitignore_text(gitignore_text)
    )
    errors: list[dict[str, str]] = []
    if pollution["replay_pollution_detected"]:
        errors.append({"field": "artifacts", "reason": "replay pollution detected"})
    if not gitignore["valid"]:
        errors.append({"field": ".gitignore", "reason": "required hygiene patterns missing"})
    return {
        "valid": not errors,
        "errors": errors,
        "pollution": pollution,
        "gitignore": gitignore,
        "mutated_repository": False,
    }


def staged_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())


def validate_staged_worktree(repo_root: Path) -> dict[str, Any]:
    gitignore_path = repo_root / ".gitignore"
    gitignore_text = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    return validate_candidate_paths(staged_paths(repo_root), gitignore_text=gitignore_text)
