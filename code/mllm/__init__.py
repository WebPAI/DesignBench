from .base import MLLMChat
from .openai_chat import OpenAIChat
from .anthropic_chat import AnthropicChat
from .mistral_chat import MistralChat
from .gemini_chat import GeminiChat
from .platform_api import DeepInfraChat, QwenChat


__all__ = [
    "MLLMChat",
    "OpenAIChat",
    "AnthropicChat",
    "MistralChat",
    "GeminiChat",
    "DeepInfraChat",
    "QwenChat",
]

def get_model(model_name: str, **kwargs) -> MLLMChat:
    match model_name:
        case "gpt-4o-2024-11-20":
            return OpenAIChat(model_name, **kwargs)
        case "claude-3-7-sonnet-20250219":
            return AnthropicChat(model_name, **kwargs)
        case "gemini-2.0-flash":
            return GeminiChat(model_name, **kwargs)
        case "qwen2.5-vl-72b-instruct" | "qwen2.5-vl-7b-instruct":
            return QwenChat(model_name, **kwargs)
        case "meta-llama/Llama-3.2-90B-Vision-Instruct" | "meta-llama/Llama-3.2-11B-Vision-Instruct":
            return DeepInfraChat(model_name, **kwargs)
        case "pixtral-large-latest" | "pixtral-12b-2409":
            return MistralChat(model_name, **kwargs)
        case _:
            raise ValueError(f"Unsupported model name: {model_name}")