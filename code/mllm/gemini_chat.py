import os
import google.generativeai as genai
from PIL import Image
from typing import List, Optional

from .base import MLLMChat

class GeminiChat(MLLMChat):
    def __init__(self, model_name: str, client: Optional[genai.GenerativeModel] = None, **kwargs) -> None:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.client = client if client else genai.GenerativeModel(model_name)
        super().__init__(model_name, **kwargs)
    
    def gemini_encode_image(self, image_path):
        return Image.open(image_path)
    
    def chat(self, system_prompt: str, prompt: str, images: Optional[List[str]] = None, stream: bool = True, print_content: bool = False) -> str:
        input_prompt = [prompt] + images if images else [prompt]
        
        model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)
        if stream:
            response_stream = model.generate_content(
                contents=input_prompt,
                generation_config=genai.GenerationConfig(
                    candidate_count=1,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
                stream=True
            )
            full_response = ""
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    if print_content:
                        print(chunk.text, end="", flush=True)
                    full_response += chunk.text
            return full_response.strip()
        else:
            response = model.generate_content(
                contents=input_prompt,
                generation_config=genai.GenerationConfig(
                    candidate_count=1,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            return response.text.strip()

