import numpy as np
from abc import ABC, abstractmethod
from typing import Any
from vpipe.core.transform import VpBaseTransform
from .payload import Payload

class ASRServiceInterface(ABC):
    @abstractmethod
    def __init__(self, lang='en', settings={}):
        """Initialize the ASR service with the specified language and settings."""
        pass

    @abstractmethod
    async def start(self):
        """Start the ASR service."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the ASR service."""
        pass

    @abstractmethod
    async def transcribe(self, buf) -> Any:
        """
        Transcribe audio buffer and return the transcription result.

        Args:
            buf (np.ndarray): Audio data in shape (frames, channels), dtype typically np.int16.
                The audio should be mono, 16kHz sample rate, and 16-bit format

        Returns:
            None: If no transcription result is available yet.
            tuple[str, bool]: (transcribed_text, is_final) if a result is available.
                - transcribed_text (str): The recognized text.
                - is_final (bool): True if this is a final result, False if partial/intermediate.
        """
        pass
        
    async def switch_lang(self, lang):
        """
        Implement this method if the service supports dynamic language switching.
        """
        raise NotImplementedError("This service does not support language setting at runtime.")


class ASRTransform(VpBaseTransform):
    """
    currently: forward silently to service in case disabled to keep ASR
    service connection alive
    future: delegate to service if it supports dynamic enabling/disabling
    """
    def __init__(self, name, service_factory, lang='en'):
        super().__init__(name=name)
        self.service_factory = service_factory
        self.service = None
        self.enable = True
        self.lang = lang
        self.wip_payload = None

    def set_service(self, service: ASRServiceInterface):
        self.service = service

    async def set_prop(self, key, value):
        match key:
            case "enable":
                self.enable = value
            case "lang":
                self.lang = value
                # 1. If service is not started, nothing to do
                if not self.service:
                    return
                # 2. At this point, service is already started
                # -> Try to switch language if supported
                try:
                    await self.service.switch_lang(value)
                # 3. Fail to switch language, don't care the reason
                #    (service does not support language switching, switching failed, ...)
                # -> Restart service to apply new language setting
                except Exception as e:
                    self.logger.warning(f"Can not switch language dynamically")
                    self.logger.warning(f"Try to restart service to apply new language")
                    # Restart service to apply new language setting
                    await self._restart_service()
                
            case _:
                raise AttributeError(f"Unknown property: {key}")

    async def _restart_service(self):
        if not self.service:
            self.logger.warning("Service is not started, cannot restart.")
            return
        
        enabled = self.enable
        self.enable = False
        await self.stop()
        await self.start()
        self.enable = enabled

    async def start(self):
        self.service = self.service_factory(lang=self.lang)
        self.logger.info(f"Starting ASR service: {self.service.__class__.__name__}")
        await self.service.start()
        self.logger.info(f"ASR service {self.service.__class__.__name__} started")

    async def stop(self):
        if self.service:
            self.logger.info(f"Stopping ASR service: {self.service.__class__.__name__}")
            await self.service.stop()
            self.logger.info(f"ASR service {self.service.__class__.__name__} stopped")

    async def transform(self, buf):
        if not self.enable:
            buf = np.zeros_like(buf)

        result = await self.service.transcribe(buf)
        if result is None:
            return None

        # At this point, we have a result from the service
        # Must ensure wip_payload is initialized
        if not self.wip_payload:
            self.wip_payload = Payload()

        # Main
        self.wip_payload.is_final = result.get("is_final", False)
        self.wip_payload.origin_text= result.get("text", None)

        # Major
        self.wip_payload.speaker = result.get("speaker", None)
        self.wip_payload.origin_audio = result.get("origin_audio", None)
        self.wip_payload.src_lang = self.lang

        # If the payload is final, we can return it
        # Then prepare for the next payload
        if self.wip_payload.is_final:
            com_payload = self.wip_payload
            self.wip_payload = Payload()
            return com_payload
        
        return self.wip_payload
