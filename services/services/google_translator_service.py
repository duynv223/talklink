import asyncio
from googletrans import Translator
from vpipe.capsules.services.tran import TranslatorServiceInterface

class GoogleTranslatorService(TranslatorServiceInterface):
    def __init__(self, **kwargs):
        self.translator = None

    def initialize(self):
        self.translator = Translator()

    async def start(self):
        await asyncio.to_thread(self.initialize)

    async def stop(self):
        pass

    async def translate(self, text: str, src: str, dest: str) -> str:
        result = await self.translator.translate(text, src=src, dest=dest)
        return result.text
