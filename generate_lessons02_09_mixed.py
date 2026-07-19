import asyncio

import generate_lesson22_mixed as generator


async def main() -> None:
    for lesson in range(2, 10):
        generator.MANIFEST = generator.ROOT / f"lesson{lesson:02d}_voice_manifest.json"
        generator.OUTPUT = generator.ROOT / "audio_output" / f"lesson{lesson:02d}_mixed"
        generator.RAW = generator.OUTPUT / "raw"
        generator.SEGMENTS = generator.OUTPUT / "segments_loud"
        generator.OUTPUT_PREFIX = f"lesson{lesson:02d}"
        await generator.main()


if __name__ == "__main__":
    asyncio.run(main())
