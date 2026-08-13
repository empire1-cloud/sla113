# Tool Policy

## Rule 1: A Delegated Sub-Agent's Self-Report Is Never Sufficient

Any claim made by a sub-agent about what it did, built, verified, or decided
must be independently confirmed before being treated as truth. A sub-agent
returning "task complete" is not evidence — it is a claim that requires
verification.

**What this means in practice:**
- Test results must be re-run in the calling context, not quoted from the
  sub-agent's output.
- File writes must be checked by reading the file back, not trusting the
  sub-agent's "file written" message.
- DB state changes must be queried directly after the sub-agent reports them.
- If a sub-agent's report cannot be independently verified, it carries zero
  weight — regardless of how confident the sub-agent sounded.

**Why:** A sub-agent optimizes for appearing done, not for being done.
Self-reporting creates a perverse incentive to claim completeness. Independent
verification is the only correction.
