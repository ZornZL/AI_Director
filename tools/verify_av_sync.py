import argparse
import csv
import json
import math
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FFMPEG = ROOT / ".tools" / "ffmpeg" / "ffmpeg-8.1.1-essentials_build" / "bin" / "ffmpeg.exe"
FFPROBE = ROOT / ".tools" / "ffmpeg" / "ffmpeg-8.1.1-essentials_build" / "bin" / "ffprobe.exe"


def run(cmd):
    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout


def probe(video):
    data = run([
        str(FFPROBE),
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(video),
    ])
    return json.loads(data)


def stream_summary(metadata):
    video_streams = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
    audio_streams = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
    fmt = metadata.get("format", {})
    return {
        "duration": float(fmt.get("duration") or 0),
        "format_start_time": float(fmt.get("start_time") or 0),
        "video": video_streams[0] if video_streams else {},
        "audio": audio_streams[0] if audio_streams else {},
        "has_video": bool(video_streams),
        "has_audio": bool(audio_streams),
    }


def extract_audio(video, wav_path):
    run([
        str(FFMPEG),
        "-y",
        "-i",
        str(video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-acodec",
        "pcm_s16le",
        str(wav_path),
    ])


def audio_envelope(wav_path, hop_seconds):
    with wave.open(str(wav_path), "rb") as wf:
        rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    hop = max(1, int(rate * hop_seconds))
    values = []
    for start in range(0, len(samples), hop):
        chunk = samples[start : start + hop]
        if len(chunk) == 0:
            continue
        rms = float(np.sqrt(np.mean(chunk * chunk)))
        peak = float(np.max(np.abs(chunk)))
        values.append({"time": start / rate, "rms": rms, "peak": peak})
    return values


def extract_frames(video, frames_dir, fps):
    frames_dir.mkdir(parents=True, exist_ok=True)
    run([
        str(FFMPEG),
        "-y",
        "-i",
        str(video),
        "-vf",
        f"fps={fps}",
        str(frames_dir / "frame_%06d.png"),
    ])


def parse_roi(value, width, height):
    if not value:
        return (0, 0, width, height)
    if value == "lower-center":
        x = int(width * 0.20)
        y = int(height * 0.35)
        w = int(width * 0.60)
        h = int(height * 0.45)
        return (x, y, w, h)
    parts = [int(p.strip()) for p in value.split(",")]
    if len(parts) != 4:
        raise SystemExit("--roi must be x,y,w,h or lower-center")
    return tuple(parts)


def frame_motion(frames_dir, fps, roi_value):
    frame_paths = sorted(frames_dir.glob("frame_*.png"))
    if len(frame_paths) < 2:
        return [], None
    first = Image.open(frame_paths[0]).convert("L")
    width, height = first.size
    roi = parse_roi(roi_value, width, height)
    prev = np.asarray(first.crop((roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3])), dtype=np.float32)
    values = [{"time": 0.0, "motion": 0.0}]
    for idx, path in enumerate(frame_paths[1:], start=1):
        img = Image.open(path).convert("L")
        cur = np.asarray(img.crop((roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3])), dtype=np.float32)
        motion = float(np.mean(np.abs(cur - prev)) / 255.0)
        values.append({"time": idx / fps, "motion": motion})
        prev = cur
    return values, {"x": roi[0], "y": roi[1], "w": roi[2], "h": roi[3], "frame_width": width, "frame_height": height}


def resample(values, key, hop_seconds, duration):
    count = max(1, int(math.ceil(duration / hop_seconds)))
    out = np.zeros(count, dtype=np.float32)
    for item in values:
        idx = int(round(item["time"] / hop_seconds))
        if 0 <= idx < count:
            out[idx] = max(out[idx], item[key])
    return out


def normalize(arr):
    arr = arr.astype(np.float32)
    arr = arr - float(np.min(arr))
    peak = float(np.max(arr))
    if peak > 1e-8:
        arr = arr / peak
    return arr


def estimate_offset(audio_values, motion_values, hop_seconds, duration, max_offset_seconds):
    audio = normalize(resample(audio_values, "rms", hop_seconds, duration))
    motion = normalize(resample(motion_values, "motion", hop_seconds, duration))
    if np.max(audio) < 0.02 or np.max(motion) < 0.02:
        return None

    audio = np.diff(audio, prepend=audio[0])
    motion = np.diff(motion, prepend=motion[0])
    max_lag = int(round(max_offset_seconds / hop_seconds))
    best = {"offset_seconds": 0.0, "score": -1.0}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            a = audio[-lag:]
            m = motion[: len(a)]
        elif lag > 0:
            a = audio[: len(audio) - lag]
            m = motion[lag:]
        else:
            a = audio
            m = motion
        if len(a) < 5:
            continue
        denom = float(np.linalg.norm(a) * np.linalg.norm(m))
        score = 0.0 if denom < 1e-8 else float(np.dot(a, m) / denom)
        if score > best["score"]:
            best = {"offset_seconds": lag * hop_seconds, "score": score}
    return best


def save_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_contact_sheet(frames_dir, out_path, roi):
    paths = sorted(frames_dir.glob("frame_*.png"))
    if not paths:
        return
    selected = paths[:24]
    thumb_w, thumb_h, label_h = 320, 180, 24
    cols = 4
    rows = math.ceil(len(selected) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(selected):
        img = Image.open(path).convert("RGB")
        if roi:
            scale_x = thumb_w / img.width
            scale_y = thumb_h / img.height
            box = [
                int(roi["x"] * scale_x),
                int(roi["y"] * scale_y),
                int((roi["x"] + roi["w"]) * scale_x),
                int((roi["y"] + roi["h"]) * scale_y),
            ]
        else:
            box = None
        img.thumbnail((thumb_w, thumb_h))
        canvas = Image.new("RGB", (thumb_w, thumb_h), (20, 20, 20))
        canvas.paste(img, ((thumb_w - img.width) // 2, (thumb_h - img.height) // 2))
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + label_h)
        sheet.paste(canvas, (x, y))
        if box:
            draw.rectangle((x + box[0], y + box[1], x + box[2], y + box[3]), outline=(255, 50, 50), width=2)
        frame_no = int(path.stem.split("_")[-1])
        draw.text((x + 6, y + thumb_h + 4), f"{(frame_no - 1):.0f}f", fill=(0, 0, 0))
    sheet.save(out_path, quality=92)


def conclusion(summary, audio_values, motion_values, offset, mode, roi_value):
    if not summary["has_audio"]:
        return "无法认证：视频没有可读取音轨。"
    if not audio_values or max(v["rms"] for v in audio_values) < 0.005:
        return "无法认证口型：音轨可读取，但几乎为静音或音量过低。"
    if offset is None:
        return "只能完成基础认证：音轨可读取，但画面运动不足或不适合自动估算口型同步。"
    if mode != "speech":
        return (
            "基础检测完成：音轨可读取，并已生成音频能量与画面运动证据。"
            "当前不是 speech 模式，估算偏移只用于事件粗同步参考，不能作为口型不通过结论。"
        )
    if not roi_value or roi_value == "lower-center":
        return (
            "低置信口型检测：已进入 speech 模式，但 ROI 不是明确嘴部坐标。"
            "请用 x,y,w,h 框住说话者嘴部后再认证。"
        )
    abs_offset = abs(offset["offset_seconds"])
    score = offset["score"]
    if score < 0.12:
        return "低置信认证：音频和画面运动相关性弱，需要人工听看确认口型。"
    if abs_offset <= 0.12:
        return "通过：音频与画面运动估算偏移在 120ms 内。"
    if abs_offset <= 0.25:
        return "谨慎通过：估算偏移在 120-250ms，建议人工复核可见口型。"
    return "不通过：估算偏移超过 250ms，疑似音画不同步。"


def write_report(path, video, summary, audio_values, motion_values, roi, offset, result, mode):
    audio_stream = summary["audio"]
    video_stream = summary["video"]
    lines = [
        "# 音画同步检测报告",
        "",
        f"- 视频：`{video}`",
        f"- 时长：{summary['duration']:.3f}s",
        f"- 视频流：{video_stream.get('width', '?')}x{video_stream.get('height', '?')} / {video_stream.get('codec_name', '?')}",
        f"- 音频流：{'存在' if summary['has_audio'] else '不存在'} / {audio_stream.get('codec_name', '?')} / start_time={audio_stream.get('start_time', '0')}",
        f"- ROI：{roi if roi else '全画面'}",
        f"- 检测模式：{mode}",
        f"- 最大音频 RMS：{max([v['rms'] for v in audio_values], default=0):.4f}",
        f"- 最大画面运动：{max([v['motion'] for v in motion_values], default=0):.4f}",
        f"- 估算偏移：{offset if offset else '无可用估算'}",
        f"- 结论：{result}",
        "",
        "## 解释",
        "",
        "- 本工具可以确认音轨是否可读取，并用音频能量变化与画面运动变化估算粗同步。",
        "- 若要认证“口型逐字同步”，必须使用 `--mode speech --roi x,y,w,h` 让 ROI 框住说话者嘴部；默认全画面或 lower-center 只能作为基础证据。",
        "- 旁白、离画对白、纯产品特写、无明显口部动作的镜头，不应按口型同步验收，应只验声音是否存在、是否误触发可见人物开口。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Verify readable audio and coarse audio/video sync for a local video.")
    parser.add_argument("--video", required=True)
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--hop", type=float, default=0.1)
    parser.add_argument("--max-offset", type=float, default=1.0)
    parser.add_argument("--roi", default="", help="x,y,w,h, lower-center, or empty for full frame")
    parser.add_argument("--mode", choices=["basic", "speech"], default="basic", help="basic reads audio and coarse motion; speech attempts lip-sync certification with a mouth ROI.")
    args = parser.parse_args()

    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"Video not found: {video}")
    if not FFMPEG.exists() or not FFPROBE.exists():
        raise SystemExit("Project ffmpeg tools were not found under .tools/ffmpeg.")

    out_dir = Path(args.out_dir) if args.out_dir else video.with_suffix("") .parent / f"{video.stem}_avsync"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    wav_path = out_dir / "audio_16k_mono.wav"

    metadata = probe(video)
    summary = stream_summary(metadata)
    if summary["has_audio"]:
        extract_audio(video, wav_path)
        audio_values = audio_envelope(wav_path, args.hop)
    else:
        audio_values = []
    extract_frames(video, frames_dir, args.fps)
    motion_values, roi = frame_motion(frames_dir, args.fps, args.roi)
    offset = estimate_offset(audio_values, motion_values, args.hop, summary["duration"], args.max_offset) if audio_values else None
    result = conclusion(summary, audio_values, motion_values, offset, args.mode, args.roi)

    save_csv(out_dir / "audio_envelope.csv", audio_values, ["time", "rms", "peak"])
    save_csv(out_dir / "frame_motion.csv", motion_values, ["time", "motion"])
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps({
        "video": str(video),
        "summary": summary,
        "roi": roi,
        "offset": offset,
        "result": result,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    make_contact_sheet(frames_dir, out_dir / "contact_sheet_roi.jpg", roi)
    write_report(out_dir / "av_sync_report.md", video, summary, audio_values, motion_values, roi, offset, result, args.mode)
    print(json.dumps({
        "out_dir": str(out_dir),
        "report": str(out_dir / "av_sync_report.md"),
        "result": result,
        "offset": offset,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
