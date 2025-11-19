import asyncio
from anthropic import AsyncAnthropic
from llm.client import LlmClient


class ClaudeClient(LlmClient):
    def __init__(self, api_key: str, model: str, temperature: float, timeout: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate(self, prompt: str) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                ),
                timeout=self.timeout
            )
            
            text_content = []
            for block in response.content:
                if block.type == "text":
                    text_content.append(block.text) # type: ignore
            
            return "\n".join(text_content) # type: ignore
        
        except asyncio.TimeoutError:
            raise Exception(f"Claude generation timed out after {self.timeout} seconds")
        
        except Exception as error:
            raise Exception(f"Claude generation failed: {error}")