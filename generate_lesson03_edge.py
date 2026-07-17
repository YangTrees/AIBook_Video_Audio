import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "lesson03_voice_manifest.json"
OUTPUT_DIR = ROOT / "audio_output" / "lesson03_edge"
RAW_DIR = OUTPUT_DIR / "raw"
SEGMENT_DIR = OUTPUT_DIR / "segments_loud"


async def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    completed = []

    for segment in manifest["segments"]:
        raw_path = RAW_DIR / f"{segment['id']}.mp3"
        output_path = SEGMENT_DIR / f"{segment['id']}.mp3"
        voice = manifest["voices"][segment["role"]]
        await edge_tts.Communicate(segment["text"], voice).save(str(raw_path))
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(raw_path),
                "-af", "loudnorm=I=-12:TP=-0.5:LRA=5",
                "-ar", "48000", "-b:a", "192k", str(output_path),
            ],
            check=True,
        )
        completed.append(output_path)
        print(f"generated: {output_path.name}")

    concat_path = OUTPUT_DIR / "concat.txt"
    concat_path.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in completed),
        encoding="utf-8",
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(OUTPUT_DIR / "lesson03_complete_loud.mp3"),
        ],
        check=True,
    )


if __name__ == "__main__":
    asyncio.run(main())

