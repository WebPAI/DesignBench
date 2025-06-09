import os
from anthropic import Anthropic
from typing import List, Optional

from .base import MLLMChat

class AnthropicChat(MLLMChat):
    def __init__(self, model_name: str, client: Optional[Anthropic] = None, **kwargs) -> None:
        self.client = client if client else Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        super().__init__(model_name, **kwargs)
    
    def construct_message(self, prompt: str):
        messages = []
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        })
        return messages
    
    def construct_images(self, prompt: str, images: List[str]):
        messages = []
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        })
        for image in images:
            messages[-1]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": f"{image}"
                },
            })
        return messages
    
    def chat(self, system_prompt: str, prompt: str, images: Optional[List[str]] = None, stream: bool = True, print_content: bool = False) -> str:
        if images:
            input_prompt = self.construct_images(prompt=prompt, images=images)
        else:
            input_prompt = self.construct_message(prompt=prompt)
        
        if stream:
            response_stream = self.client.messages.create(
                model=self.model_name,
                messages=input_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                stream=True
            )
            full_response = ""
            for event in response_stream:
                if event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta" and delta.text:
                        if print_content:
                            print(delta.text, end="", flush=True)
                        full_response += delta.text
            return full_response.strip()
        else:
            response = self.client.messages.create(
                model=self.model_name,
                messages=input_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt
            )
            return response.content[0].text.strip()
