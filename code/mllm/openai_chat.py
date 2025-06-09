import os
from openai import OpenAI
from typing import List, Optional

from .base import MLLMChat

class OpenAIChat(MLLMChat):
    def __init__(self, model_name: str, client: Optional[OpenAI] = None, **kwargs) -> None:
        self.client = client if client else OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        super().__init__(model_name, **kwargs)
    
    def chat(self, system_prompt: str, prompt: str, images: Optional[List[str]] = None, stream: bool = True, print_content: bool = False) -> str:
        if images:
            input_prompt = self.construct_images(system_prompt=system_prompt, prompt=prompt, images=images)
        else:
            input_prompt = self.construct_message(system_prompt=system_prompt, prompt=prompt)
        
        if stream:
            response_stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=input_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                seed=self.seed,
                stream=True
            )
            full_response = ""
            for chunk in response_stream:
                if chunk.choices and hasattr(chunk.choices[0], "delta"):
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        if print_content:
                            print(delta.content, end="", flush=True)
                        full_response += delta.content
            return full_response.strip()
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=input_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                seed=self.seed
            )
            return response.choices[0].message.content.strip()
