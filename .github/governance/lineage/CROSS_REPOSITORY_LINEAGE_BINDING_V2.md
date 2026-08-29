# CROSS_REPOSITORY_LINEAGE_BINDING_V2

## Status

Human-ratified, exactly pinned, and replay-safe.

This revision records the current binding between the stable SAPIANTA development root and its separately versioned `sapianta_system` governance dependency. It reuses the V1 cross-repository lineage mechanism and preserves V1 unchanged as historical evidence.

## Deterministic Pairing

- root repository: `git@github.com:Aljosa3/sapianta-ecosystem.git`
- root commit: `2fb0b645fd883faf53a08ab07c0311906fc4d4f2`
- root tree: `bd32263838a11bc7143b1b5cb77da5c4afc94629`
- nested repository: `git@github.com:Aljosa3/sapianta-core.git`
- immutable acquisition ref: `refs/tags/sapianta-system-nested-authority-3183bab-v1`
- nested commit: `3183bab71f8f30397c0309dd2e6d846d14a11f66`
- nested tree: `7c32ec05efc2be43297849bc38ec8766514a523d`
- binding id: `CROSS-REPOSITORY-LINEAGE-BINDING-5aa7cafa62e7b57c5bf1487e`
- binding hash: `cba57d82855302f1834da36913f68498bc482921aea55d1a064dd8e59d6abeb9`
- canonical JSON hash: `5aa7cafa62e7b57c5bf1487e75bd35c9271c67273c800a060d159f26fa638ad1`

## Pinning Policy

The nested dependency is acquired from the immutable tag and used at the exact commit and tree above. It is checked out detached. No mutable branch may automatically advance this binding.

Every source, tag, commit, tree, or checkout-state mismatch fails closed.

## Human Ratification Provenance

G77-256FT supplies explicit Human ratification for this exact source, immutable tag, commit, tree, and pinning policy. Its supplied instruction bytes have SHA-256 `3c3189b9eff93c7732dd88b8cd9b2a4a8723df4f0a0b5ca0abf5de86e6c0819c`. G77-256FS is the preceding durable publication generation.

This provenance authorizes root-to-nested binding and stable-worktree provisioning only.

## Mutation Boundaries

- does not authorize P11 or E05;
- does not authorize execution, providers, Trusted Access, or production;
- does not change runtime behavior;
- does not create a production route;
- becomes read-only historical lineage after commit; and
- preserves `CROSS_REPOSITORY_LINEAGE_BINDING_V1` without modification.
