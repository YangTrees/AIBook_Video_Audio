import asyncio

import generate_lesson22_mixed as generator


generator.MANIFEST = generator.ROOT / "lesson26_voice_manifest.json"
generator.OUTPUT = generator.ROOT / "audio_output" / "lesson26_mixed"
generator.RAW = generator.OUTPUT / "raw"
generator.SEGMENTS = generator.OUTPUT / "segments_loud"
generator.OUTPUT_PREFIX = "lesson26"


if __name__ == "__main__":
    asyncio.run(generator.main())
