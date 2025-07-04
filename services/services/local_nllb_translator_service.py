import httpx
import logging
import json
from vpipe.capsules.services.tran import TranslatorServiceInterface
logger = logging.getLogger(__name__)

class LocalNLLBTranslatorService(TranslatorServiceInterface):
    def __init__(self, settings={}):
        logger.info(f"Initializing LocalNLLBTranslatorService with settings: {settings}")
        self.base_url = settings.get('url', 'http://10.133.134.206:8011')
        self.client = None

    async def start(self):
        self.client = httpx.AsyncClient(base_url=self.base_url)
        logger.info(f"LocalNLLBTranslator connect to server: {self.base_url}")

    async def stop(self):
        await self.client.aclose()

    async def translate(self, text: str, src: str, dest: str) -> str:
        payload = {
            "text": text,
            "src_lang": src,
            "tgt_lang": dest
        }
        try:
            logger.info(f"Send REQ translate to server: {self.base_url}, payload: {json.dumps(payload)}")
            response = await self.client.post("/translated", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("translated_text")
        except httpx.HTTPStatusError as e:
            logger.error(f"Translation failed: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Error communicating with translation service: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during translation: {str(e)}")
            return None