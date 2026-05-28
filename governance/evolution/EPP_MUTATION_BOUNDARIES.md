# EPP_MUTATION_BOUNDARIES
Status: GOVERNANCE FOUNDATION
Layer: Constitutional Evolution Governance
Principle: Protected Layers Are Not Proposal Targets

---

# 1. PURPOSE

This artifact defines mutation boundaries for future EPP proposals.

It does not grant mutation authority.

---

# 2. LOCKED LAYERS

The following layers are locked for EPP mutation proposals unless a
separate constitutional process explicitly authorizes review:

- governance;
- replay;
- ledger;
- constitutional rules;
- approval systems;
- governance evidence;
- replay history;
- fail-closed enforcement.

Locked layers are not runtime tuning surfaces.

---

# 3. CONTROLLED LAYERS

The following layers may become proposal targets only under bounded,
sandboxed, replay-visible, reversible review:

- bounded runtime modules;
- configurable policies;
- scoring parameters;
- thresholds;
- validation parameters;
- documented operational constraints.

Controlled layers remain non-mutable until a separate promotion decision
authorizes a specific bounded change.

---

# 4. FORBIDDEN EVOLUTION ACTIONS

EPP proposals MUST NOT recommend or enable:

- self-expanding authority;
- disabling replay;
- disabling fail-closed behavior;
- removing approval gates;
- modifying governance evidence;
- mutation of replay history;
- uncontrolled recursive evolution;
- hidden runtime mutation;
- autonomous self-promotion;
- protected-layer mutation;
- unbounded provider authority.

---

# 5. EVOLUTION SCOPE RULES

Every evolution proposal MUST be:

- bounded in scope;
- isolated to a sandbox;
- replay-visible;
- reversible;
- evidence-backed;
- explicitly reviewed;
- blocked on uncertainty.

Any uncertainty:

-> BLOCK evolution proposal

---

# 6. BOUNDARY CONCLUSION

EPP may analyze controlled-layer changes. It may not mutate locked
layers, bypass approval, or convert analysis into execution authority.
