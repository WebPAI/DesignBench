import base64
from typing import Union, List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv(override=True)

class MLLMChat:
    DEFAULT_MAX_TOKENS = 8192 * 2
    DEFAULT_TEMPERATURE = 0
    DEFAULT_SEED = 42
    
    def __init__(self, model_name: str, **kwargs) -> None:
        self.model_name = model_name
        self.max_tokens = kwargs.get("max_tokens", self.DEFAULT_MAX_TOKENS)
        self.temperature = kwargs.get("temperature", self.DEFAULT_TEMPERATURE)
        self.seed = kwargs.get("seed", self.DEFAULT_SEED)
        print(f"Temperature: {self.temperature}, Max Tokens: {self.max_tokens}, Seed: {self.seed}")
        
    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def construct_message(self, system_prompt: str, prompt: str) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        return messages
    
    def construct_images(self, system_prompt: str, prompt: str, images: List[str]) -> List[Dict[str, Any]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        for image in images:
            messages[-1]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",
                        "detail": "high"
                    },
                }
            )
        return messages

    def chat(self, system_prompt: str, prompt: str, images: Optional[List[str]] = None, stream: bool = True, print_content: bool = False) -> str:
        pass
