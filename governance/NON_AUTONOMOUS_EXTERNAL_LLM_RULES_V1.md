# NON_AUTONOMOUS_EXTERNAL_LLM_RULES_V1
Status: NON-AUTONOMOUS EXTERNAL LLM RULES
Layer: Governance Discovery

---

# 1. RULE PURPOSE

This artifact defines the non-autonomous boundary for external LLM
interaction.

External LLM interaction is bounded evidence exchange, not agency.

---

# 2. NON-AUTONOMOUS RULES

An external LLM interaction may:

- provide bounded contribution evidence;
- expose provider metadata;
- produce replay-visible proposal text;
- support governance review;
- preserve deterministic lineage.

An external LLM interaction may not:

- execute;
- authorize;
- orchestrate;
- plan autonomously;
- mutate governance;
- create hidden runtime memory;
- delegate authority to itself;
- bypass human or governance approval.

---

# 3. AUTHORITY BOUNDARY

External LLM output is non-authoritative.

External LLM ingress does not grant execution authority.

External LLM egress does not grant orchestration authority.

External LLM lineage does not grant governance mutation authority.
