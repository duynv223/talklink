import asyncio
from vpipe.core.composite import VpComposite
from vpipe.core.capsule import VpState
from vpipe.core.config import GLOBAL_AUDIO_CONFIG
from vpipe.capsules.audio.audio_mixer import VpAudiopMixer
from vpipe.capsules.audio.file_source import VpFileSource
from vpipe.capsules.audio.speaker_sink import VpSpeakerSink


async def main():
    pipeline = VpComposite("audio_mixer_pipeline")

    # Create
    mixer = VpAudiopMixer()
    src1 = VpFileSource('assets/sample.mp3', audio_config=GLOBAL_AUDIO_CONFIG)
    src2 = VpFileSource('assets/sample-1.mp3', audio_config=GLOBAL_AUDIO_CONFIG)
    speaker = VpSpeakerSink(audio_config=GLOBAL_AUDIO_CONFIG)

    # Add
    pipeline.add(src1)
    pipeline.add(src2)
    pipeline.add(mixer)
    pipeline.add(speaker)

    # Connect
    src1 >> mixer.add_input('i1')
    src2 >> mixer.add_input('i2')
    mixer >> speaker

    # Run
    await pipeline.set_state(VpState.RUNNING)
    await asyncio.sleep(20)
    await pipeline.set_state(VpState.PAUSED)


if __name__ == "__main__":
    asyncio.run(main())
