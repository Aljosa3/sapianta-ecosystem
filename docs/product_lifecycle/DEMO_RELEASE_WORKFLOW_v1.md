# SAPIANTA Demo Release Workflow v1

## Document Role

This document defines conservative practical steps for updating the stable Product 1 demo runtime.

This workflow is documentation-only. It does not deploy automatically, push automatically, or modify runtime semantics.

## Scope

Product 1 is the AI Decision Validator.

The demo server is a controlled showcase node. Development happens locally first, stable source state is recorded in GitHub, and the server is updated only after a stable checkpoint and release decision.

## 1. Develop Locally

Work from the local PC workspace:

```bash
cd ~/work/sapianta
git status
```

Keep productization work focused on demo UX, audit UX, replay UX, explainability UX, EU AI Act positioning, and unknown-decision governance presentation.

Do not use the server as the experimentation environment.

## 2. Create Feature Branch

Create a feature branch for Product 1 work:

```bash
git switch -c feature/product-1-demo-ux
```

If a relevant feature branch already exists:

```bash
git switch feature/product-1-demo-ux
```

## 3. Validate Locally

Run lightweight local checks appropriate for the files changed.

Examples:

```bash
git status
```

```bash
git diff --check
```

For documentation-only changes, inspect the changed files directly:

```bash
git diff -- docs/ artifacts/ runtime/governance/master/
```

If the product application has lightweight tests available, run only the safe local test command documented by that repository.

## 4. Commit

Review the changed files:

```bash
git status
git diff
```

Commit only the intended changes:

```bash
git add docs/product_lifecycle artifacts/product_lifecycle runtime/governance/master/ROADMAP.md runtime/governance/master/CURRENT_FOCUS.md
git commit -m "Document product lifecycle architecture v1"
```

## 5. Push to GitHub

Push the reviewed feature branch:

```bash
git push -u origin feature/product-1-demo-ux
```

Do not push automatically from local tooling. The human operator decides when the source state is ready.

## 6. Release Decision

Before server update, confirm:
- local validation passed
- changed files are intentional
- runtime semantics are untouched
- foundation architecture is preserved
- GitHub contains the intended stable checkpoint
- demo update is desired now

Optional release branch:

```bash
git switch -c release/product-1-demo-v1
git push -u origin release/product-1-demo-v1
```

## 7. Pull on Server

On the Hetzner demo server, pull only after the stable checkpoint and release decision.

Example:

```bash
cd /path/to/sapianta
git status
git pull --ff-only
```

Use the actual server path and branch selected for the demo runtime. If the server worktree has unexpected local changes, stop and inspect before proceeding.

## 8. Restart Demo Service

Restart only the intended demo service using the known service command for the server.

Example pattern:

```bash
sudo systemctl restart sapianta-demo
```

Use the real service name. Do not restart unrelated services.

## 9. Verify Homepage

Verify that the Product 1 homepage loads and communicates the enterprise demo narrative:
- AI Decision Validator
- EU AI Act execution governance
- enterprise trust
- auditability
- replayability

Example:

```bash
curl -I https://demo.example.com/
```

Use the real demo URL.

## 10. Verify Audit Viewer

Verify that the audit viewer loads and shows the expected demo evidence.

Example:

```bash
curl -I https://demo.example.com/audit
```

Use the real audit viewer path.

## 11. Verify Swagger/API Docs

Verify Swagger or API documentation after restart.

Example:

```bash
curl -I https://demo.example.com/docs
```

Use the real Swagger/API docs path.

## 12. Record Demo Release Note

Record a short release note for the demo checkpoint.

Minimum content:
- release name
- date
- source branch or commit
- scope of change
- validation performed
- known limitations
- confirmation that no runtime governance activation occurred

Release notes should be append-only product lineage where practical.
