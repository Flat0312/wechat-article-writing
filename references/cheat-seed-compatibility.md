# Cheat seed humanizer compatibility register

The external `cheat-seed` route currently mentions a generic `humanizer`
Skill, while this WeChat total-control workflow declares `humanizer-zh` as
the only optional diagnostic Skill. This is an external contract mismatch;
the total-control repository does not rewrite the external route.

When invoking the real root `cheat-on-content` Skill for `cheat-seed`:

- Do not install, discover, or invoke a second Skill named `humanizer` because
  of text emitted by the external route.
- Keep the root Cheat seed result scoped to topic seeding. It is not a
  humanizer diagnostic and cannot replace the `humanizer-zh` contract in
  [`humanizer-diagnostic-contract.md`](humanizer-diagnostic-contract.md).
- If the external seed route hard-blocks on its generic humanizer dependency,
  mark the seed stage `failed` or `blocked`, preserve the raw failure, and do
  not simulate a candidate or continue as if `humanizer-zh` satisfied it.
- If the seed route completes without using that branch, record the external
  mismatch in the execution notes and continue only with the real root result.

This register is a boundary adaptation, not a claim that the external
`cheat-seed` implementation has been fixed. The external route must be updated
separately to name `humanizer-zh` or to remove that dependency.
