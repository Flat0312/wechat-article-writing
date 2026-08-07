from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import tempfile


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "article-project-template"
SCHEMA_VERSION_1_0 = "1.0"
SCHEMA_VERSION_1_1 = "1.1"
STAGES = (
    "brief",
    "topic",
    "evidence",
    "outline",
    "draft",
    "final",
    "prediction",
    "visual_plan",
    "visuals",
    "html",
    "publish",
    "retro",
)
STAGES_1_1 = (
    "brief",
    "topic",
    "evidence",
    "outline",
    "draft",
    "final",
    "prediction",
    "publish",
    "retro",
)
STAGES_BY_SCHEMA = {
    SCHEMA_VERSION_1_0: STAGES,
    SCHEMA_VERSION_1_1: STAGES_1_1,
}


def _stages_for(state):
    return STAGES_BY_SCHEMA.get(state.get("schema_version"), STAGES)
ALLOWED_STATUS = {
    "pending",
    "in_progress",
    "awaiting_confirmation",
    "completed",
    "failed",
    "skipped",
    "stale",
}
STATE_FIELDS = frozenset(
    {
        "schema_version",
        "article_id",
        "mode",
        "profile_ref",
        "cheat_binding",
        "current_stage",
        "stage_status",
        "artifacts",
        "approvals",
        "skill_routes",
        "stale_artifacts",
        "required_actions",
        "created_at",
        "updated_at",
    }
)
FORBIDDEN_FIELD_PARTS = (
    "secret",
    "token",
    "cookie",
    "password",
    "credential",
    "body",
    "content",
)


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _portable_profile_ref(value: str | None) -> str | None:
    if value is None:
        return None
    raw = str(value)
    windows_path = PureWindowsPath(raw)
    portable_path = PurePosixPath(raw.replace("\\", "/"))
    if (
        not raw
        or windows_path.anchor
        or portable_path.is_absolute()
        or ".." in portable_path.parts
        or portable_path == PurePosixPath(".")
    ):
        raise ValueError("profile_ref must be a portable relative reference")
    return portable_path.as_posix()


def _logical_cheat_binding(value: str | None) -> str | None:
    if value is None:
        return None
    binding = str(value)
    if (
        not binding
        or not binding[0].isalnum()
        or not binding[-1].isalnum()
        or ".." in binding
        or any(
            not (character.isalnum() or character in "._-")
            for character in binding
        )
    ):
        raise ValueError("cheat_binding must be a logical identifier")
    return binding


def _validate_state_fields(state: dict[str, object]) -> None:
    schema_version = state.get("schema_version")
    if schema_version not in STAGES_BY_SCHEMA:
        raise ValueError(
            f"article state schema_version must be one of {sorted(STAGES_BY_SCHEMA)}"
        )
    expected_stages = STAGES_BY_SCHEMA[schema_version]
    status_keys = set((state.get("stage_status") or {}).keys())
    if status_keys and status_keys != set(expected_stages):
        raise ValueError(
            f"stage_status keys must match schema {schema_version} stages"
        )
    unknown = set(state) - STATE_FIELDS
    if unknown:
        has_secret_like = any(
            isinstance(key, str)
            and any(part in key.lower() for part in FORBIDDEN_FIELD_PARTS)
            for key in unknown
        )
        if has_secret_like:
            raise ValueError("secret-like or body fields are not allowed in article state")
        names = ", ".join(sorted(map(str, unknown)))
        raise ValueError(f"unknown article state fields: {names}")
    missing = STATE_FIELDS - set(state)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"missing article state fields: {names}")
    if _portable_profile_ref(state["profile_ref"]) != state["profile_ref"]:
        raise ValueError("profile_ref in article state must use POSIX separators")
    if _logical_cheat_binding(state["cheat_binding"]) != state["cheat_binding"]:
        raise ValueError("cheat_binding in article state must be a logical identifier")


def load_state(project: Path) -> dict[str, object]:
    project = Path(project).resolve()
    state_path = project / "article-state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8-sig"))
    _validate_state_fields(payload)
    return payload


def write_state(project: Path, state: dict[str, object]) -> None:
    _validate_state_fields(state)
    updated_at = _now()
    persisted = dict(state)
    persisted["updated_at"] = updated_at
    payload = json.dumps(persisted, ensure_ascii=False, indent=2) + "\n"
    project_root = Path(project).resolve()
    state_path = project_root / "article-state.json"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=".article-state.json.tmp-",
            dir=project_root,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, state_path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    state["updated_at"] = updated_at


def create_project(
    project: Path,
    article_id: str,
    mode: str,
    profile_ref: str | None,
    cheat_binding: str | None = None,
) -> dict[str, object]:
    profile_ref = _portable_profile_ref(profile_ref)
    cheat_binding = _logical_cheat_binding(cheat_binding)
    project = Path(project).expanduser().resolve()
    if project.exists():
        raise FileExistsError(project)
    project.parent.mkdir(parents=True, exist_ok=True)
    if project.exists():
        raise FileExistsError(project)

    temporary_root = Path(
        tempfile.mkdtemp(prefix=f".{project.name}.tmp-", dir=project.parent)
    ).resolve()
    if temporary_root.parent != project.parent:
        raise RuntimeError("temporary article root escaped the project parent")
    staging = temporary_root / "article"
    try:
        shutil.copytree(TEMPLATE_ROOT, staging)
        (staging / "output").mkdir(exist_ok=True)
        (staging / "visuals" / "assets").mkdir(exist_ok=True)
        timestamp = _now()
        state = {
            "schema_version": "1.0",
            "article_id": article_id,
            "mode": mode,
            "profile_ref": profile_ref,
            "cheat_binding": cheat_binding,
            "current_stage": "brief",
            "stage_status": {stage: "pending" for stage in STAGES},
            "artifacts": {},
            "approvals": {},
            "skill_routes": {},
            "stale_artifacts": [],
            "required_actions": [],
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        write_state(staging, state)
        if project.exists():
            raise FileExistsError(project)
        staging.rename(project)
        return state
    finally:
        if temporary_root.parent == project.parent:
            shutil.rmtree(temporary_root, ignore_errors=True)


def create_project_v11(
    project: Path,
    article_id: str,
    mode: str,
    profile_ref: str | None,
    cheat_binding: str | None = None,
) -> dict[str, object]:
    profile_ref = _portable_profile_ref(profile_ref)
    cheat_binding = _logical_cheat_binding(cheat_binding)
    project = Path(project).expanduser().resolve()
    if project.exists():
        raise FileExistsError(project)
    project.parent.mkdir(parents=True, exist_ok=True)

    temporary_root = Path(
        tempfile.mkdtemp(prefix=f".{project.name}.tmp-", dir=project.parent)
    ).resolve()
    if temporary_root.parent != project.parent:
        raise RuntimeError("temporary article root escaped the project parent")
    staging = temporary_root / "article"
    try:
        shutil.copytree(TEMPLATE_ROOT, staging)
        # schema 1.1 不走 HTML 五件套 / 视觉轨道，删除模板中仅 1.0 使用的
        # output/ 与 visuals/ 顶层目录，避免给新项目制造空的 1.0 资产骨架。
        shutil.rmtree(staging / "output", ignore_errors=True)
        shutil.rmtree(staging / "visuals", ignore_errors=True)
        now = _now()
        state: dict[str, object] = {
            "schema_version": SCHEMA_VERSION_1_1,
            "article_id": article_id,
            "mode": mode,
            "profile_ref": profile_ref,
            "cheat_binding": cheat_binding,
            "current_stage": "brief",
            "stage_status": {stage: "pending" for stage in STAGES_1_1},
            "artifacts": {},
            "approvals": {},
            "skill_routes": {},
            "stale_artifacts": [],
            "required_actions": [],
            "created_at": now,
            "updated_at": now,
        }
        write_state(staging, state)
        if project.exists():
            raise FileExistsError(project)
        staging.rename(project)
    finally:
        if temporary_root.parent == project.parent:
            shutil.rmtree(temporary_root, ignore_errors=True)
    return state


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_artifact(
    state: dict[str, object], project: Path, role: str, relative_path: Path
) -> dict[str, object]:
    relative_path = Path(relative_path)
    if (
        relative_path.is_absolute()
        or relative_path.anchor
        or ".." in relative_path.parts
    ):
        raise ValueError("artifact path must be relative to the article project")

    project_root = Path(project).resolve()
    target = project_root / relative_path
    try:
        resolved_target = target.resolve(strict=True)
        resolved_target.relative_to(project_root)
    except FileNotFoundError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError("artifact path escapes the article project") from error

    if not resolved_target.is_file():
        raise FileNotFoundError(target)
    artifact_hash = file_hash(resolved_target)
    previous_artifact = state["artifacts"].get(role)
    previous_hash = (
        previous_artifact.get("sha256")
        if isinstance(previous_artifact, dict)
        else None
    )
    state["artifacts"][role] = {
        "path": relative_path.as_posix(),
        "sha256": artifact_hash,
    }
    if previous_hash is not None and previous_hash != artifact_hash:
        state["approvals"] = {
            key: approval
            for key, approval in state["approvals"].items()
            if not (
                isinstance(approval, dict)
                and approval.get("artifact_role") == role
            )
        }
    if role in state["stage_status"]:
        state["stage_status"][role] = "completed"
    state["stale_artifacts"] = [
        stale_role for stale_role in state["stale_artifacts"] if stale_role != role
    ]
    if role == "prediction":
        state["required_actions"] = [
            action
            for action in state["required_actions"]
            if action != "create_new_prediction_version"
        ]
    write_state(Path(project), state)
    return state


def set_stage(
    state: dict[str, object], stage: str, status: str
) -> dict[str, object]:
    if stage not in _stages_for(state):
        raise ValueError(f"unknown stage: {stage}")
    if status not in ALLOWED_STATUS:
        raise ValueError(f"unknown status: {status}")
    state["current_stage"] = stage
    state["stage_status"][stage] = status
    return state


def record_approval(
    state: dict[str, object],
    key: str,
    approved_at: str,
    artifact_role: str | None = None,
) -> dict[str, object]:
    if key == "final":
        if artifact_role is None:
            artifact_role = "final"
        elif artifact_role != "final":
            raise ValueError("final approval must bind the final artifact")

    approval = {"approved": True, "approved_at": approved_at}
    if artifact_role is not None:
        artifact = state["artifacts"].get(artifact_role)
        if not isinstance(artifact, dict) or not artifact.get("sha256"):
            if key == "final":
                raise ValueError("final artifact must be recorded before approval")
            raise ValueError(
                f"artifact must be recorded before approval: {artifact_role}"
            )
        approval["artifact_role"] = artifact_role
        approval["artifact_sha256"] = artifact["sha256"]
    state["approvals"][key] = approval
    return state


def record_route(
    state: dict[str, object], action: str, skill_name: str
) -> dict[str, object]:
    state["skill_routes"][action] = skill_name
    return state


def invalidate_from(state: dict[str, object], stage: str) -> dict[str, object]:
    stages = _stages_for(state)
    if stage not in stages:
        raise ValueError(f"unknown stage: {stage}")
    invalidated_stages = set(stages[stages.index(stage) :])
    state["approvals"] = {
        key: approval
        for key, approval in state["approvals"].items()
        if not (
            key in invalidated_stages
            or (
                isinstance(approval, dict)
                and approval.get("artifact_role") in invalidated_stages
            )
        )
    }
    start = stages.index(stage) + 1
    for downstream in stages[start:]:
        has_artifact = downstream in state["artifacts"]
        if state["stage_status"].get(downstream) == "completed" or has_artifact:
            state["stage_status"][downstream] = "stale"
        if (
            has_artifact
            and downstream not in state["stale_artifacts"]
        ):
            state["stale_artifacts"].append(downstream)
    if (
        "prediction" in stages[start:]
        and "create_new_prediction_version" not in state["required_actions"]
    ):
        state["required_actions"].append("create_new_prediction_version")
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init")
    init.add_argument("project", type=Path)
    init.add_argument("--article-id", required=True)
    init.add_argument("--mode", choices=("full", "fast", "temporary"), required=True)
    init.add_argument(
        "--schema-version",
        choices=(SCHEMA_VERSION_1_1, SCHEMA_VERSION_1_0),
        default=SCHEMA_VERSION_1_1,
    )
    init.add_argument("--profile-ref")
    init.add_argument("--cheat-binding")
    stage = subparsers.add_parser("set-stage")
    stage.add_argument("project", type=Path)
    stage.add_argument("--stage", choices=STAGES + STAGES_1_1, required=True)
    stage.add_argument("--status", choices=sorted(ALLOWED_STATUS), required=True)
    approve = subparsers.add_parser("approve")
    approve.add_argument("project", type=Path)
    approve.add_argument("--key", required=True)
    approve.add_argument("--approved-at", required=True)
    approve.add_argument("--artifact-role")
    route = subparsers.add_parser("route")
    route.add_argument("project", type=Path)
    route.add_argument("--action", required=True)
    route.add_argument("--skill", required=True)
    record = subparsers.add_parser("record")
    record.add_argument("project", type=Path)
    record.add_argument("--role", required=True)
    record.add_argument("--path", type=Path, required=True)
    invalidate = subparsers.add_parser("invalidate")
    invalidate.add_argument("project", type=Path)
    invalidate.add_argument("--stage", choices=STAGES + STAGES_1_1, required=True)
    args = parser.parse_args()
    if args.command == "init":
        if args.schema_version == SCHEMA_VERSION_1_1:
            state = create_project_v11(
                args.project,
                args.article_id,
                args.mode,
                args.profile_ref,
                args.cheat_binding,
            )
        else:
            state = create_project(
                args.project,
                args.article_id,
                args.mode,
                args.profile_ref,
                args.cheat_binding,
            )
    else:
        state_path = args.project / "article-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if args.command == "set-stage":
            set_stage(state, args.stage, args.status)
        elif args.command == "approve":
            record_approval(
                state,
                args.key,
                args.approved_at,
                args.artifact_role,
            )
        elif args.command == "route":
            record_route(state, args.action, args.skill)
        elif args.command == "record":
            record_artifact(state, args.project, args.role, args.path)
        else:
            invalidate_from(state, args.stage)
        if args.command != "record":
            write_state(args.project, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
