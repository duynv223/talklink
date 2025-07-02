import asyncio
from functools import partial
from vpipe.core.pipeline import VpPipeline
from pipelines.downstream_pipeline import DownStreamPipeline
from pipelines.upstream_pipeline import UpStreamPipeline


class DualStreamPipeline(VpPipeline):
    def __init__(self, name="dual-stream-pipeline", 
                 script_writer_callback=None,
                 translated_script_writer_callback=None,
                 rms_callback=None):
        super().__init__(name)
        self.scr_writter = script_writer_callback or (lambda *args: None)
        self.translated_scr_writter = translated_script_writer_callback or (lambda *args: None)
        self.rms_callback = rms_callback or (lambda stream, rms: None)

        self._downstream = DownStreamPipeline(
            name="downstream",
            script_writer_callback=partial(self.scr_writter, "Other"),
            translated_script_writer_callback=partial(self.translated_scr_writter, "Other"),
            rms_callback=partial(self.rms_callback, "downstream")
        )
        self._upstream = UpStreamPipeline(
            name="upstream",
            script_writer_callback=partial(self.scr_writter, "You"),
            translated_script_writer_callback=partial(self.translated_scr_writter, "You"),
            rms_callback=partial(self.rms_callback, "upstream")
        )

        self.adds(self._upstream, self._downstream)

    @property
    def upstream(self):
        return self._upstream
    
    @property
    def downstream(self):
        return self._downstream
    