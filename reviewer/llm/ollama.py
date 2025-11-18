import aiohttp
from typing import TypedDict

from llm.client import LlmClient


class OllamaGenerateRequest(TypedDict):
    model: str
    prompt: str
    stream: bool
    temperature: float


class OllamaClient(LlmClient):

    def __init__(self, host: str, model: str, temperature: float, timeout: int):
        self.host = host
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    async def generate(self, prompt: str) -> str:
        url = f"http://{self.host}/api/generate"
        
        request_body: OllamaGenerateRequest = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=request_body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Ollama returned status {response.status}: {error_text}"
                    )
                
                response_data = await response.json()
                return response_data.get("response", "")