import asyncio
import logging
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from vpipe.capsules.services.asr import ASRServiceInterface


logger = logging.getLogger(__name__)

LANG_MODEL_MAP = {
    "en": {"model": "nova-3", "language": "en"},
    "ja": {"model": "nova-2-general", "language": "ja"},
    "vi": {"model": "nova-2-general", "language": "vi"},
}

class DeepGramASRService(ASRServiceInterface):
    def __init__(self, lang='en', settings={}):
        logger.debug(f"Initializing Deepgram ASR service with lang: {lang}, settings: {settings}")
        self.lang = lang if lang in LANG_MODEL_MAP else "en"
        self.model = LANG_MODEL_MAP[self.lang]["model"]
        self.language = LANG_MODEL_MAP[self.lang]["language"]
        self.utterance_end_ms = int(settings.get("utterance_end_ms", "1024"))
        self.endpointing = int(settings.get("endpointing", "300"))

        self.client = DeepgramClient(api_key=settings.get("api_key") or "")
        self.conn = self.client.listen.asyncwebsocket.v("1")
        self.recv_queue = asyncio.Queue()
        self.buffer = bytearray()
        self.started = False
        self.min_send_size = 1024 * 16

        self.conn.on(LiveTranscriptionEvents.Transcript, self._on_transcript)

    async def _on_transcript(self, *args, **kwargs):
        result = kwargs.get("result")
        if result is None:
            return

        logger.debug(f"Received transcript: {result}")
        sentence = result.channel.alternatives[0].transcript
        if sentence:
            await self.recv_queue.put((sentence, result.is_final))

    async def start(self):
        if not self.started:
            options = LiveOptions(
                model=self.model,
                language=self.language,
                smart_format=True,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
                interim_results=True,
                utterance_end_ms=self.utterance_end_ms,
                vad_events=True,
                endpointing=self.endpointing,
            )
            logger.debug(f"Starting Deepgram ASR service with options: {options}")
            if not await self.conn.start(options):
                raise RuntimeError("Failed to connect to Deepgram")
            logger.debug("Deepgram ASR service started successfully")
            self.started = True

    async def stop(self):
        logger.debug("Stopping Deepgram ASR service")
        if self.started:
            await self.conn.finish()
            logger.debug("Deepgram ASR service stopped successfully")
            self.started = False

    async def transcribe(self, audio: bytes) -> tuple[str, bool]:
        if not self.started:
            return None
        
        self.buffer += audio.tobytes()
        if len(self.buffer) >= self.min_send_size:
            await self.conn.send(self.buffer)
            self.buffer = bytearray()

        try:
            result, is_final = self.recv_queue.get_nowait()
            return result, is_final
        except asyncio.QueueEmpty:
            return None

