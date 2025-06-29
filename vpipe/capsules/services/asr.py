import numpy as np
from abc import ABC, abstractmethod
from typing import Any
from vpipe.core.transform import VpBaseTransform


class ASRServiceInterface(ABC):
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


class ASRTransform(VpBaseTransform):
    """
    currently: forward silently to service in case disabled to keep ASR
    service connection alive
    future: delegate to service if it supports dynamic enabling/disabling
    """
    def __init__(self, name, service: ASRServiceInterface):
        super().__init__(name=name)
        self.service = service
        self.enable = True

    def set_service(self, service: ASRServiceInterface):
        self.service = service

    def set_prop(self, key, value):
        match key:
            case "enable":
                self.enable = value
            case _:
                raise AttributeError(f"Unknown property: {key}")

    async def start(self):
        print(f"Starting ASR service: {self.service.__class__.__name__}")
        await self.service.start()
        print(f"ASR service {self.service.__class__.__name__} started")

    async def stop(self):
        print(f"Stopping ASR service: {self.service.__class__.__name__}")
        await self.service.stop()
        print(f"ASR service {self.service.__class__.__name__} stopped")

    async def transform(self, buf):
        if not self.enable:
            buf = np.zeros_like(buf)
        return await self.service.transcribe(buf)
