# Post-migrate Cheat status receipt

`cheat-migrate` changes the source project's `.cheat-state.json`, but its own
workflow does not produce a machine-readable compatibility receipt. The total
control therefore requires a fresh root `cheat-status` call after every
successful migration. The root call must normalize its result into this input
shape before handing it to the adapter:

```json
{
  "source": "cheat-status",
  "target_project_binding": "primary",
  "cheat_schema_version": "1.2",
  "status": "compatible",
  "checked_at": "2026-08-05T15:00:00+08:00"
}
```

The adapter independently reads `<CHEAT_PROJECT>/.cheat-state.json` and rejects
the receipt when its `schema_version` differs. It also rejects a non-compatible
status, another source, a missing timezone, or a machine path disguised as a
binding. `target_project_binding` is a logical name such as `primary`; it is
not a filesystem path.

Run it only after the real `cheat-migrate` and the fresh root `cheat-status`:

```text
python <SKILL_ROOT>/scripts/cheat_status_adapter.py record <ACCOUNT_DIR> --cheat-project <CHEAT_PROJECT> --status-receipt <CHEAT_STATUS.json> --target-binding primary
python <SKILL_ROOT>/scripts/cheat_status_adapter.py verify <ACCOUNT_DIR>/cheat-status-receipt.json --cheat-project <CHEAT_PROJECT> --target-binding primary
```

The successful output is `<ACCOUNT_DIR>/cheat-status-receipt.json`:

| Field | Required value |
|---|---|
| `schema_version` | `1.0` (receipt schema) |
| `receipt_type` | `post-migrate-cheat-status` |
| `target_project_binding` | The confirmed logical binding, for example `primary` |
| `cheat_schema_version` | The version reported by `cheat-status` and the live state file |
| `status` | `compatible` |
| `source` | `cheat-status` |
| `checked_at` | Timezone-aware ISO 8601 timestamp |

The receipt is evidence of a fresh compatible status check, not a substitute
for invoking the root Cheat Skill. Import or downstream work must stop when the
receipt is absent or `verify` fails.
