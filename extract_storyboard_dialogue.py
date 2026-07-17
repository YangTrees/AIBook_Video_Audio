import json
import re
import sys
from pathlib import Path


ROLE_MAP = {"团团": "tuantuan", "点点": "diandian", "旁白": "narrator"}
SCENE_RE = re.compile(r"^###\s*(\d+)\.\s*.*?(\d{2}:\d{2})-(\d{2}:\d{2})", re.M)
ROLE_RE = re.compile(r"^(团团|点点|旁白)(?:（[^）]*）|\([^)]*\))?\s*[：:]\s*(.*)$")


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^[“\"]|[”\"]$', "", text)
    text = text.replace('"', "“")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_file(path: Path, episode: str) -> list[dict]:
    content = path.read_text(encoding="utf-8-sig")
    matches = list(SCENE_RE.finditer(content))
    segments = []
    counters = {}

    for index, match in enumerate(matches):
        scene = int(match.group(1))
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        block = content[match.end():block_end]
        lines = block.splitlines()
        in_dialogue = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("台词/旁白：") or stripped.startswith("台词/旁白:"):
                in_dialogue = True
                rest = re.split(r"台词/旁白[：:]", stripped, maxsplit=1)[1].strip()
                if rest:
                    role_match = ROLE_RE.match(rest)
                    if role_match:
                        role_name, text = role_match.groups()
                    else:
                        role_name, text = "旁白", rest
                    text = clean_text(text)
                    if text and text != "...":
                        counters[(scene, role_name)] = counters.get((scene, role_name), 0) + 1
                        segments.append(make_segment(episode, scene, role_name, text, counters))
                continue
            if stripped in {"台词：", "台词:"}:
                in_dialogue = True
                continue
            if not in_dialogue:
                continue
            if stripped.startswith(("画面：", "关键帧：", "---", "## ", "### ")):
                break
            role_match = ROLE_RE.match(stripped)
            if role_match:
                role_name, text = role_match.groups()
                text = clean_text(text)
                if text and text != "...":
                    counters[(scene, role_name)] = counters.get((scene, role_name), 0) + 1
                    segments.append(make_segment(episode, scene, role_name, text, counters))

    return segments


def make_segment(episode, scene, role_name, text, counters):
    count = counters[(scene, role_name)]
    suffix = f"_{count:02d}" if count > 1 else ""
    role = ROLE_MAP[role_name]
    return {
        "id": f"{episode}_{scene:02d}_{role}{suffix}",
        "episode": episode,
        "scene": scene,
        "role": role,
        "text": text,
    }


def main():
    if len(sys.argv) != 5:
        raise SystemExit("Usage: extract_storyboard_dialogue.py LESSON TITLE UPPER LOWER")
    lesson, title, upper, lower = sys.argv[1:]
    result = {
        "lesson": f"第{lesson}课-{title}",
        "voices": {
            "tuantuan": {"provider": "edge", "voice_id": "zh-CN-YunxiaNeural"},
            "diandian": {
                "provider": "minimax",
                "voice_id": "AIBook_diandian_edge_20260715174438",
                "speed": 0.98,
                "vol": 1.0,
                "pitch": 1,
                "emotion": "happy",
            },
            "narrator": {
                "provider": "edge",
                "voice_id": "zh-CN-XiaoxiaoNeural",
            },
        },
        "segments": extract_file(Path(upper), "upper") + extract_file(Path(lower), "lower"),
    }
    output = Path(f"lesson{int(lesson):02d}_voice_manifest.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
