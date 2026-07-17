import asyncio
from pathlib import Path

import generate_lesson22_mixed as generator


generator.MANIFEST = generator.ROOT / "lesson23_voice_manifest.json"
generator.OUTPUT = generator.ROOT / "audio_output" / "lesson23_mixed"
generator.RAW = generator.OUTPUT / "raw"
generator.SEGMENTS = generator.OUTPUT / "segments_loud"
generator.OUTPUT_PREFIX = "lesson23"


if __name__ == "__main__":
    asyncio.run(generator.main())
