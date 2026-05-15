# Real Interaction Ingress/Egress Adapter v1

This package accepts one deterministic local JSON ingress artifact and exports one deterministic local JSON egress artifact.

It attaches local artifact continuity to the interaction transport bridge and fails closed when ingress or egress lineage is incomplete. It does not monitor directories, run daemons, expose APIs, or add async behavior.
