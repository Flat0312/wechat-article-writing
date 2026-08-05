# Offline external contract fixtures

`tests/fixtures/external_contracts.json` is an offline normalized boundary
fixture. It does not call a network service or claim that an external Skill
returned these values in production. It models the input, output path receipt,
and status receipt that the total-control Skill accepts at each seam.

The fixture test covers:

- all ten external Skills used by this workflow;
- the five topic signal lanes, including the local Xiaohongshu override;
- long-essay Cheat prediction, publish, and retro receipt paths;
- the bounded Khazix and humanizer responses;
- one static 21:9 cover and the five HTML delivery files.

When an external Skill changes its real output shape, update the external
Skill and this fixture in the same change review. A fixture passing only proves
that the total-control adapter still rejects/accepts the declared boundary; it
does not replace the mandatory real Skill invocation.
