from typing import Tuple, List, Union, Dict
from utils import Framework, Mode

EDIT_SYSTEM_PROMPT = """
{introduction}
{provide_items}
You need to modify the code according to the user's instruction to make the webpage satisfy user's demands.

Requirements:
- Do not modify any part of the web page other than the parts covered by the instructions.
- For images, use placeholder images from https://placehold.co
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.

{output_message}

Do not output any extra information or comments.
"""


def get_design_edit_prompt(framework: Framework, mode: Mode, instruction: str, code: Union[str, Dict]) -> Tuple[str, str]:
    
    if framework == Framework.VANILLA:
        introduction = "You are an expert HTML/CSS developer."
        output_message = f"You MUST wrap your entire code output inside the following markdown fences: ```html and ```."
        code_message = f"Code:\n{code}"
    elif framework == Framework.REACT:
        introduction = "You are an expert React/Tailwind developer."
        output_message = f"You MUST wrap your entire code output inside the following markdown fences: ```jsx and ```."
        code_message = f"Code:\n{code}"
    elif framework == Framework.VUE:
        introduction = "You are an expert Vue/Tailwind developer."
        output_message = f"You MUST wrap your entire code output inside the following markdown fences: ```vue and ```."
        code_message = f"Code:\n{code}"
    elif framework == Framework.ANGULAR:
        introduction = "You are an expert Angular/Tailwind developer."
        output_message = f"You MUST wrap your TypeScript component code inside the following markdown fences: ```ts and ```;\n"
        output_message += f"You MUST wrap your HTML template code inside the following markdown fences: ```angular and ```.\n"
        output_message += "***CRITICAL INSTRUCTION: Your response MUST ALWAYS include both the HTML and TypeScript code.***"
        html_code, ts_code = code["html"], code["ts"]
        code_message = f"The HTML code:\n```angular\n{html_code}\n```\nThe TypeScript code:\n```ts\n{ts_code}\n```"
    
    if mode == Mode.BOTH:
        provide_items = "You take a screenshot, a piece of code of a reference web page, and an instruction from the user."
        prompt = f"Instruction: {instruction}\n\n{code_message}\n\nThe webpage screenshot:\n"
    elif mode == Mode.IMAGE:
        provide_items = "You take a screenshot, and an instruction from the user."
        prompt = f"Instruction: {instruction}\n\nThe webpage screenshot:\n"
    elif mode == Mode.CODE:
        provide_items = "You take a piece of code of a reference web page, and an instruction from the user."
        prompt = f"Instruction: {instruction}\n\n{code_message}"
    else:
        raise ValueError(f"Unsupported mode: {mode.value}")
    
    system_prompt = EDIT_SYSTEM_PROMPT.format(
        introduction=introduction,
        provide_items=provide_items,
        output_message=output_message
    ).strip()
        
        
    return system_prompt, prompt