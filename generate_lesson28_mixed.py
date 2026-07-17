import asyncio

import generate_lesson22_mixed as generator


generator.MANIFEST = generator.ROOT / "lesson28_voice_manifest.json"
generator.OUTPUT = generator.ROOT / "audio_output" / "lesson28_mixed"
generator.RAW = generator.OUTPUT / "raw"
generator.SEGMENTS = generator.OUTPUT / "segments_loud"
generator.OUTPUT_PREFIX = "lesson28"


if __name__ == "__main__":
    asyncio.run(generator.main())

