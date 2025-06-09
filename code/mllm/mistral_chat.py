import os
from mistralai import Mistral
from typing import List, Optional

from .base import MLLMChat

class MistralChat(MLLMChat):
    def __init__(self, model_name: str, client: Optional[Mistral] = None, **kwargs) -> None:
        self.client = client if client else Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        super().__init__(model_name, **kwargs)
    
    def chat(self, system_prompt: str, prompt: str, images: Optional[List[str]] = None, stream: bool = True, print_content: bool = False) -> str:
        if images:
            input_prompt = self.construct_images(system_prompt=system_prompt, prompt=prompt, images=images)
        else:
            input_prompt = self.construct_message(system_prompt=system_prompt, prompt=prompt)
        
        if stream:
            response_stream = self.client.chat.stream(
                model=self.model_name,
                messages=input_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                random_seed=self.seed
            )
            full_response = ""
            for chunk in response_stream:
                if hasattr(chunk.data.choices[0].delta, "content") and chunk.data.choices[0].delta.content:
                    if print_content:
                        print(chunk.data.choices[0].delta.content, end="", flush=True)
                    full_response += chunk.data.choices[0].delta.content
            return full_response.strip()
        else:
            response = self.client.chat.complete(
                model=self.model_name,
                messages=input_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                random_seed=self.seed
            )
            return response.choices[0].message.content.strip()
