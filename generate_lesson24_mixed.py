import asyncio

import generate_lesson22_mixed as generator


generator.MANIFEST = generator.ROOT / "lesson24_voice_manifest.json"
generator.OUTPUT = generator.ROOT / "audio_output" / "lesson24_mixed"
generator.RAW = generator.OUTPUT / "raw"
generator.SEGMENTS = generator.OUTPUT / "segments_loud"
generator.OUTPUT_PREFIX = "lesson24"


if __name__ == "__main__":
    asyncio.run(generator.main())
