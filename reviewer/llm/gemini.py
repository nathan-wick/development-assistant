import asyncio
from google import genai
from google.genai import types

from llm.client import LlmClient


class GeminiClient(LlmClient):

    def __init__(self, api_key: str, model: str, temperature: float, timeout: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.client = genai.Client(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content( # type: ignore
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=self.temperature
                        )
                    )
                ),
                timeout=self.timeout
            )
            
            return response.text or ""
        
        except asyncio.TimeoutError:
            raise Exception(f"Gemini generation timed out after {self.timeout} seconds")
        
        except Exception as error:
            raise Exception(f"Gemini generation failed: {error}")