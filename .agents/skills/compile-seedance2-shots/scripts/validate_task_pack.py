#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT_REQUIRED = {"project_id", "model_profile", "source_lock", "production_assumptions", "bibles", "assets", "asset_generation_tasks", "shots"}
SHOT_REQUIRED = {
    "shot_id", "source_ids", "purpose", "duration_seconds", "aspect_ratio",
    "input_mode", "references", "keyframes", "first_frame", "camera", "blocking",
    "performance", "audio", "voice_continuity", "timeline", "edit_handles", "lighting_environment", "end_frame",
    "continuity_from", "negative_constraints", "prompt", "acceptance", "fallback",
}
INPUT_MODES = {"text", "image", "audio", "video", "mixed"}


def nonempty(value):
    return value not in (None, "", [], {})


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ["top level must be an object"], warnings

    missing_root = sorted(ROOT_REQUIRED - set(data))
    if missing_root:
        errors.append("missing project fields: " + ", ".join(missing_root))
    if "tasks" in data or "clips" in data:
        errors.append("use only the top-level 'shots' array; tasks/clips are not allowed")

    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        errors.append("shots must be a non-empty array")
        return errors, warnings

    seen = set()
    for index, shot in enumerate(shots, 1):
        label = f"shot {index}"
        if not isinstance(shot, dict):
            errors.append(f"{label}: must be an object")
            continue
        missing = sorted(SHOT_REQUIRED - set(shot))
        if missing:
            errors.append(f"{label}: missing {', '.join(missing)}")
        empty = sorted(key for key in SHOT_REQUIRED if key in shot and not nonempty(shot[key]) and key not in {"references", "continuity_from"})
        if empty:
            errors.append(f"{label}: empty {', '.join(empty)}")

        shot_id = shot.get("shot_id")
        if shot_id in seen:
            errors.append(f"{label}: duplicate shot_id {shot_id}")
        seen.add(shot_id)

        duration = shot.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool):
            errors.append(f"{label}: duration_seconds must be numeric")
        elif not 4 <= duration <= 15:
            errors.append(f"{label}: duration_seconds must be between 4 and 15")

        if shot.get("input_mode") not in INPUT_MODES:
            errors.append(f"{label}: invalid input_mode")

        audio = shot.get("audio")
        if not isinstance(audio, dict):
            errors.append(f"{label}: audio must be an object")
        elif audio.get("dialogue"):
            for key in ("speaker", "addressee"):
                if not nonempty(audio.get(key)):
                    errors.append(f"{label}: dialogue requires audio.{key}")
            for key in ("lip_sync", "non_speakers_closed_mouth"):
                if audio.get(key) is not True:
                    errors.append(f"{label}: dialogue requires audio.{key}=true")

        timeline = shot.get("timeline")
        if not isinstance(timeline, list) or not timeline:
            errors.append(f"{label}: timeline must be a non-empty array")
        elif isinstance(duration, (int, float)) and duration <= 10 and len(timeline) > 6:
            warnings.append(f"{label}: probable action overload")

        handles = shot.get("edit_handles")
        if not isinstance(handles, dict):
            errors.append(f"{label}: edit_handles must be an object")
        else:
            for key in ("head_seconds", "tail_seconds"):
                value = handles.get(key)
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    errors.append(f"{label}: edit_handles.{key} must be numeric")
            for key in ("head_state", "tail_state", "cut_note"):
                if not nonempty(handles.get(key)):
                    errors.append(f"{label}: edit_handles.{key} is required")
            tail = handles.get("tail_seconds")
            if isinstance(tail, (int, float)) and not isinstance(tail, bool) and tail < 0.2:
                warnings.append(f"{label}: tail edit handle is shorter than 0.2s")

        refs = shot.get("references")
        if not isinstance(refs, list):
            errors.append(f"{label}: references must be an array")
        else:
            counts = {"image": 0, "audio": 0, "video": 0}
            for ref in refs:
                if not isinstance(ref, dict) or not nonempty(ref.get("asset_id")) or not nonempty(ref.get("type")) or not nonempty(ref.get("purpose")):
                    errors.append(f"{label}: each reference requires asset_id, type and purpose")
                    continue
                if ref["type"] in counts:
                    counts[ref["type"]] += 1
            limits = {"image": 9, "audio": 3, "video": 3}
            for kind, limit in limits.items():
                if counts[kind] > limit:
                    errors.append(f"{label}: {kind} references exceed limit {limit}")

        keyframes = shot.get("keyframes")
        if not isinstance(keyframes, dict):
            errors.append(f"{label}: keyframes must be an object")
        else:
            first = keyframes.get("first")
            if not isinstance(first, dict) or not nonempty(first.get("prompt")) or not nonempty(first.get("acceptance")):
                errors.append(f"{label}: keyframes.first requires prompt and acceptance")

        prompt = shot.get("prompt", "")
        for marker in ("【任务与时长】", "【首帧】", "【摄影】", "【逐秒时间轴】", "【剪辑手柄】", "【尾帧】", "【禁止】"):
            if marker not in prompt:
                warnings.append(f"{label}: prompt missing marker {marker}")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    errors, warnings = validate(data)
    print(json.dumps({"shots": len(data.get("shots", [])) if isinstance(data, dict) else 0, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
