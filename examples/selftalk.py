import asyncio
from vpipe.core.capsule import VpState
from pipelines.selftalk_pipeline import SelfTalkPipeline

"""
This example demonstrates how to use the SelfTalkPipeline capsule to transcribe
and translate from microphone input.
It sets up a pipeline that listens to audio input, transcribes it, and translates the text.
Note: set Deepgram API key in environment variable `DEEPGRAM_API_KEY` before running this example.
```
$env:DEEPGRAM_API_KEY="your-deepgram-api-key"
```
"""


def write_script(text, is_final):
    if text:
        if is_final:
            print(f"\033[94mTranscribed text: {text}, Final: {is_final}\033[0m")
        else:
            print(f"Transcribed text: {text}, Final: {is_final}")    


def write_translated_script(text):
    print(f"\033[92mTranslated text: {text}\033[0m")


async def main():
    pipeline = SelfTalkPipeline(
        name="selftalk-pipeline",
        script_writer_callback=write_script,
        translated_script_writer_callback=write_translated_script
    )

    await pipeline.set_prop('src-lang', 'en')
    await pipeline.set_prop('dest-lang', 'vi')

    await pipeline.set_state(VpState.RUNNING)
    await asyncio.Event().wait()
    

if __name__ == "__main__":
    asyncio.run(main())