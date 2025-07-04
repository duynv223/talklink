from abc import ABC, abstractmethod
from vpipe.core.transform import VpBaseTransform
from .payload import Payload

class TTSServiceInterface(ABC):
    @abstractmethod
    def __init__(self, settings={}):
        """Initialize the tts service with optional settings."""
        pass

    @abstractmethod
    async def start(self):
        """Start the TTS service."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the TTS service."""
        pass

    @abstractmethod
    async def synthesize(self, text: str, lang: str, ref_voice: bytearray = None, speaker_id: str = None) -> bytes:
        """
        Synthesize speech from the given text and return audio data.
        Returns:
            np.ndarray: Audio data in shape (frames, channels), dtype typically np.int16
            Refer to vpipe.core.config for audio format details.
        """
        pass


class TTSTransform(VpBaseTransform):
    def __init__(self, name=None, service_factory=None, lang='en'):
        super().__init__(name=name)
        self.service_factory = service_factory
        self.service = None
        self.lang = lang
        self.enable = True

    def set_service(self, service: TTSServiceInterface):
        self.service = service

    async def set_prop(self, key: str, value):
        match key:
            case 'lang':
                self.lang = value
            case 'enable':
                self.enable = value
            case _:
                raise ValueError(f"Unknown property: {key}")
    
    async def get_prop(self, key: str):
        match key:
            case 'lang':
                return self.lang
            case _:
                raise ValueError(f"Unknown property: {key}")

    async def start(self):
        self.service = self.service_factory()
        self.logger.info(f"Starting TTS service: {self.service.__class__.__name__}")
        await self.service.start()
        self.logger.info(f"TTS service {self.service.__class__.__name__} started")

    async def stop(self):
        if self.service:
            self.logger.info(f"Stopping TTS service: {self.service.__class__.__name__}")
            await self.service.stop()
            self.logger.info(f"TTS service {self.service.__class__.__name__} stopped")

    async def transform(self, data: Payload) -> bytes:
        if self.enable:
            if not data or not data.is_final or not data.translated_text:
                return None
            data.translated_audio = await self.service.synthesize(
                text=data.translated_text,
                lang=data.dest_lang,
                ref_voice=data.origin_audio,
                speaker_id=data.speaker
            )
            return data.translated_audio
