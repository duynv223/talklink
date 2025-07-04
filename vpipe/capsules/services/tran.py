from abc import ABC, abstractmethod
from vpipe.core.transform import VpBaseTransform


class TranslatorServiceInterface(ABC):
    @abstractmethod
    def __init__(self, settings={}):
        """Initialize the translator service with optional settings."""
        pass

    @abstractmethod
    async def start(self):
        """Start the translator service."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the translator service."""
        pass

    @abstractmethod
    async def translate(self, text: str, src: str, dest: str) -> str:
        """Translate the given text and return the translated result."""
        pass


class TranslationTransform(VpBaseTransform):
    def __init__(self, name=None, service_factory=None, src: str = 'en', dest: str = 'vi'):
        super().__init__(name=name)
        self.service_factory = service_factory
        self.service = None
        self.src = src
        self.dest = dest

    def set_service(self, service: TranslatorServiceInterface):
        self.service = service

    async def set_prop(self, key: str, value):
        match key:
            case 'src-lang':
                self.src = value
            case 'dest-lang':
                self.dest = value
            case _:
                raise ValueError(f"Unknown property: {key}")
    
    def get_prop(self, key: str):
        match key:
            case 'src-lang':
                return self.src
            case 'dest-lang':
                return self.dest
            case _:
                raise ValueError(f"Unknown property: {key}")

    async def start(self):
        self.service = self.service_factory()
        self.logger.info(f"Starting translation service: {self.service.__class__.__name__}")
        await self.service.start()
        self.logger.info(f"Translation service {self.service.__class__.__name__} started")

    async def stop(self):
        if self.service:
            self.logger.info(f"Stopping translation service: {self.service.__class__.__name__}")
            await self.service.stop()
            self.logger.info(f"Translation service {self.service.__class__.__name__} stopped")

    async def transform(self, text) -> str:
        translated_text = await self.service.translate(text, src=self.src, dest=self.dest)
        return translated_text