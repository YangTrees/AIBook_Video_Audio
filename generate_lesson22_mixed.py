import asyncio
import json
import subprocess
import urllib.request
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "lesson22_voice_manifest.json"
OUTPUT = ROOT / "audio_output" / "lesson22_mixed"
RAW = OUTPUT / "raw"
SEGMENTS = OUTPUT / "segments_loud"
OUTPUT_PREFIX = "lesson22"


def read_env() -> dict[str, str]:
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def minimax_tts(text: str, voice: dict, env: dict[str, str], output: Path) -> None:
    payload = {
        "model": env["MINIMAX_TTS_MODEL"],
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice["voice_id"],
            "speed": voice["speed"],
            "vol": voice["vol"],
            "pitch": voice["pitch"],
            "emotion": voice["emotion"],
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
        "subtitle_enable": False,
        "aigc_watermark": False,
    }
    request = urllib.request.Request(
        env["MINIMAX_BASE_URL"].rstrip("/") + "/v1/t2a_v2",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {env['MINIMAX_API_KEY']}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        result = json.load(response)
    if result["base_resp"]["status_code"] != 0 or result["data"]["status"] != 2:
        raise RuntimeError(result["base_resp"]["status_msg"])
    output.write_bytes(bytes.fromhex(result["data"]["audio"]))


def normalize(source: Path, output: Path, role: str) -> None:
    filters = {
        "diandian": "highpass=f=100,equalizer=f=380:t=q:w=0.9:g=-2.5,equalizer=f=950:t=q:w=1.0:g=-1.5,equalizer=f=2900:t=q:w=1.1:g=2.8,equalizer=f=5200:t=q:w=1.0:g=2.0,acompressor=threshold=0.10:ratio=2.6:attack=4:release=70:makeup=1.6,loudnorm=I=-11:TP=-0.5:LRA=4",
        "narrator": "loudnorm=I=-11.5:TP=-0.5:LRA=5",
        "tuantuan": "loudnorm=I=-12:TP=-0.5:LRA=5",
    }
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(source), "-af", filters[role],
            "-ar", "48000", "-b:a", "192k", str(output),
        ],
        check=True,
    )


async def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    env = read_env()
    RAW.mkdir(parents=True, exist_ok=True)
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    episode_paths = {"upper": [], "lower": []}

    for segment in manifest["segments"]:
        voice = manifest["voices"][segment["role"]]
        raw_path = RAW / f"{segment['id']}.mp3"
        output_path = SEGMENTS / f"{segment['id']}.mp3"
        if voice["provider"] == "edge":
            await edge_tts.Communicate(
                segment["text"],
                voice["voice_id"],
                rate=voice.get("rate", "+0%"),
                pitch=voice.get("pitch", "+0Hz"),
                volume=voice.get("volume", "+0%"),
            ).save(str(raw_path))
        else:
            await asyncio.to_thread(minimax_tts, segment["text"], voice, env, raw_path)
        normalize(raw_path, output_path, segment["role"])
        episode_paths[segment["episode"]].append(output_path)
        print(f"generated: {output_path.name}")

    for episode, paths in episode_paths.items():
        concat_file = OUTPUT / f"{episode}_concat.txt"
        concat_file.write_text(
            "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "concat", "-safe", "0", "-i", str(concat_file),
                "-c:a", "libmp3lame", "-b:a", "192k",
                str(OUTPUT / f"{OUTPUT_PREFIX}_{episode}_complete.mp3"),
            ],
            check=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
