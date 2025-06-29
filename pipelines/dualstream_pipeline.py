import asyncio
from functools import partial
from vpipe.core.pipeline import VpPipeline
from pipelines.downstream_pipeline import DownStreamPipeline
from pipelines.upstream_pipeline import UpStreamPipeline


class DualStreamPipeline(VpPipeline):
    def __init__(self, name="dual-stream-pipeline", 
                 script_writer_callback=None,
                 translated_script_writer_callback=None):
        """
        Args:
            name (str): Pipeline name.
            script_writer_callback (callable): (event_type: str, speaker: str, text: str) -> None
                event_type: "transcribe" or "translate"
                speaker: speaker name or role
                text: transcript or translation
        """

        super().__init__(name)
        self.scr_writter = script_writer_callback or (lambda *args: None)
        self.translated_scr_writter = translated_script_writer_callback or (lambda *args: None)

        self.downstream = DownStreamPipeline(
            name="downstream",
            script_writer_callback=partial(self.scr_writter, "Other"),
            translated_script_writer_callback=partial(self.translated_scr_writter, "Other"),
        )
        self.upstream = UpStreamPipeline(
            name="upstream",
            script_writer_callback=partial(self.scr_writter, "You"),
            translated_script_writer_callback=partial(self.translated_scr_writter, "You"),
        )

        self.adds(self.upstream, self.downstream)

    async def set_prop(self, prop, value):
        match prop:
            case "other-lang":
                await self.downstream.set_prop("src-lang", value)
                await self.upstream.set_prop("dest-lang", value)
            case "your-lang":
                await self.downstream.set_prop("dest-lang", value)
                await self.upstream.set_prop("src-lang", value)
            case "src-volume" | "tts-volume":
                await self.upstream.set_prop(prop, value)
                await self.downstream.set_prop(prop, value)
            case _:
                raise ValueError(f"Unknown property: {prop}")
