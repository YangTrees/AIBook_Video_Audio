import asyncio

import generate_lesson22_mixed as generator


async def main():
    for lesson in range(28, 33):
        prefix = f"lesson{lesson:02d}"
        generator.MANIFEST = generator.ROOT / f"{prefix}_voice_manifest.json"
        generator.OUTPUT = generator.ROOT / "audio_output" / f"{prefix}_mixed"
        generator.RAW = generator.OUTPUT / "raw"
        generator.SEGMENTS = generator.OUTPUT / "segments_loud"
        generator.OUTPUT_PREFIX = prefix
        print(f"=== generating {prefix} ===")
        await generator.main()


if __name__ == "__main__":
    asyncio.run(main())

