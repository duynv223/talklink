import asyncio
from vpipe.core.pipeline import VpPipeline
from vpipe.core.capsule import VpState
from vpipe.capsules.audio.file_source import VpFileSource
from vpipe.capsules.audio.speaker_sink import VpSpeakerSink
from vpipe.capsules.audio.volume import VpVolume


async def main():
    pipeline = VpPipeline("hello_vpipe")
    src = VpFileSource('assets/sample-1.mp3')
    sink = VpSpeakerSink()
    volume = VpVolume(0.2)
    src >> volume >> sink

    pipeline.adds(src, sink, volume)
    await pipeline.set_state(VpState.RUNNING)
    await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())
