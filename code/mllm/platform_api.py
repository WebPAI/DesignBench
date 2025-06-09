import os
from openai import OpenAI
from typing import List, Optional

from mllm.openai_chat import OpenAIChat

class DeepInfraChat(OpenAIChat):
    def __init__(self, model_name: str, **kwargs) -> None:
        client = OpenAI(
            api_key=os.getenv(f"DEEPINFRA_API_KEY"),
            base_url="https://api.deepinfra.com/v1/openai",
        )
        super().__init__(model_name, client, **kwargs)
    
    def chat(self, system_prompt: str, prompt: str, images: Optional[List[str]] = None, stream: bool = True, print_content: bool = False) -> str:
        # For stability, the system instructions are better to be put in the user prompt.
        prompt = f"{system_prompt}\n\n{prompt}\n\n"
        system_prompt = "Your are a helpful assistant."
        return super().chat(system_prompt, prompt, images, stream, print_content)


class GeminiChat(OpenAIChat):
    def __init__(self, model_name: str, **kwargs) -> None:
        client = OpenAI(
            api_key=os.getenv(f"GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        super().__init__(model_name, client, **kwargs)


class QwenChat(OpenAIChat):
    def __init__(self, model_name: str, **kwargs) -> None:
        client = OpenAI(
            api_key=os.getenv(f"QWEN_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        max_tokens = 8192   # Max tokens for Qwen models
        super().__init__(model_name, client, max_tokens=max_tokens, **kwargs)
