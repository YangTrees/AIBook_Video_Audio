import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "lesson20_voice_manifest.json"
OUTPUT_DIR = ROOT / "audio_output" / "lesson20_edge"
RAW_DIR = OUTPUT_DIR / "raw"
SEGMENT_DIR = OUTPUT_DIR / "segments"
TARGET_I = -16
TARGET_TP = -1
TARGET_LRA = 7


async def synthesize(segment: dict, voice: str) -> Path:
    raw_path = RAW_DIR / f"{segment['id']}.mp3"
    communicate = edge_tts.Communicate(segment["text"], voice)
    await communicate.save(str(raw_path))
    return raw_path


def normalize(raw_path: Path, output_path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(raw_path),
            "-af",
            f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}",
            "-ar",
            "48000",
            "-b:a",
            "192k",
            str(output_path),
        ],
        check=True,
    )


def make_concat(episode: str, paths: list[Path]) -> None:
    list_path = OUTPUT_DIR / f"{episode}_concat.txt"
    list_path.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
    )
    output_path = OUTPUT_DIR / f"lesson20_{episode}_complete.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ],
        check=True,
    )


async def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    episode_paths = {"upper": [], "lower": []}

    for segment in manifest["segments"]:
        voice = manifest["voices"][segment["role"]]
        raw_path = await synthesize(segment, voice)
        output_path = SEGMENT_DIR / f"{segment['id']}.mp3"
        normalize(raw_path, output_path)
        episode_paths[segment["episode"]].append(output_path)
        print(f"generated: {output_path.name}")

    for episode, paths in episode_paths.items():
        make_concat(episode, paths)


if __name__ == "__main__":
    asyncio.run(main())
