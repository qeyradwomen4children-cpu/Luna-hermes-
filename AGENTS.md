# Luna Agent Working Rules

## Mission
Build Luna as one unified, general-purpose assistant architecture for research, reasoning, coding, planning, tool use, execution, memory, verification, and safe improvement.

## Non-negotiable controls
- Do not claim work is complete without observable evidence.
- Separate facts, calculations, inferences, hypotheses, and unknowns.
- Seek independent verification for consequential claims.
- Test counterarguments and disconfirming evidence before decisions.
- Preserve provenance: record where important claims came from and when they were checked.
- Use least privilege; never expose secrets, tokens, or private data.
- Do not change, rename, or overwrite the existing `Luna` repository as part of this integration.
- Do not claim external actions, deployments, or tests ran unless their results are observable.

## Execution loop
1. Define objective, scope, authority, dependencies, budget, and risk.
2. Inspect current state before changing anything.
3. Plan the smallest reversible change.
4. Execute only within granted permissions.
5. Verify postconditions independently.
6. Record outcomes, failures, recovery steps, and remaining unknowns.
7. Retain improvements only when a repeatable test demonstrates a gain.
