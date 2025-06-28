import asyncio
from vpipe.core.capsule import VpState
from pipelines.downstream_pipeline import DownStreamPipeline
from pipelines.upstream_pipeline import UpStreamPipeline


async def main():
    def script_writer_callback(text, is_final):
        print(f"Script: {text} (final: {is_final})")

    def translated_script_writer_callback(translated_text):
        print(f"Translated Script: {translated_text}")

    upstream_pipeline = UpStreamPipeline(
        script_writer_callback=script_writer_callback,
        translated_script_writer_callback=translated_script_writer_callback
    )

    downstream_pipeline = DownStreamPipeline(
        script_writer_callback=script_writer_callback,
        translated_script_writer_callback=translated_script_writer_callback
    )

    await downstream_pipeline.set_prop('src-lang', 'en')
    await downstream_pipeline.set_prop('dest-lang', 'vi')
    await upstream_pipeline.set_prop('src-lang', 'vi')
    await upstream_pipeline.set_prop('dest-lang', 'en')

    await upstream_pipeline.set_state(VpState.RUNNING)
    await downstream_pipeline.set_state(VpState.RUNNING)

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
