from typing import Union, Dict, Tuple
from utils import Framework, Mode

COMPILE_ERROR_REPAIR_VUE_PROMPT = """
You are an expert Vue/Tailwind developer.
You are proficient in UI Code Repair.
You take a piece of code with compile error and the compile error information.
You need to repair the compile error.

Requirements:
- Do not modify the code except for the part with compile errors.
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code.

Here is the code with compile error:
{code}

{error_info}
PLease repair the code and output it wrapped inside the following markdown fences: ```vue and ```.
"""

COMPILE_ERROR_REPAIR_REACT_PROMPT = """
You are an expert React/Tailwind developer.
You are proficient in UI Code Repair.
You take a piece of code with compile error and the compile error information.
You need to repair the compile error.

Requirements:
- Do not modify the code except for the part with compile errors.
- Do not add placeholder comments such as "// Add other navigation links as needed" or "// ... other logic ..." in place of actual code. Write the complete, correct code.

Here is the code with compile error:
{code}

{error_info}
Please repair the code and output it wrapped inside the following markdown fences: ```jsx and ```.
"""

COMPILE_ERROR_REPAIR_ANGULAR_PROMPT = """
You are an expert Angular/Tailwind developer.
You are proficient in UI Code Repair using TypeScript and Angular templates.
You take a component's code (HTML/TypeScript) with a compile error and the associated error information.
You need to repair the compile error.

Requirements:
- Do not modify the code except for the part with compile errors.
- Do not add placeholder comments like "<!-- Add other navigation links as needed -->" or "// ... other logic ..." in place of real code. Write the actual corrected code.

Here is the code with compile error:
{code}

{error_info}
Please repair the code and output it wrapped inside the following markdown fences: ```ts and ``` for TypeScript, and ```html and ``` for Angular templates.
YOU NEED TO OUTPUT BOTH HTML AND TS CODE.
"""


def get_design_compile_repair_prompt(framework: Framework, mode: Mode, code: Union[str, Dict], error_info: str) -> Tuple[str, str]:
    
    system_prompt = "You are a helpful assistant."
    
    if framework == Framework.VUE:
        prompt_template = COMPILE_ERROR_REPAIR_VUE_PROMPT.strip()
        code = f"```vue\n{code}\n```"
    elif framework == Framework.REACT:
        prompt_template = COMPILE_ERROR_REPAIR_REACT_PROMPT.strip()
        code = f"```jsx\n{code}\n```"
    elif framework == Framework.ANGULAR:
        prompt_template = COMPILE_ERROR_REPAIR_ANGULAR_PROMPT.strip()
        code = f"```angular\n{code['html']}\n```\n```ts\n{code['ts']}\n```"
    else:
        raise ValueError(f"Unsupported framework: {framework}")
    
    if mode == Mode.CODE:
        prompt = prompt_template.format(code=code, error_info="")
    elif mode == Mode.BOTH:
        error_info = f"The compile error information is as follows: \"{error_info}\"\n"
        prompt = prompt_template.format(code=code, error_info=error_info)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    return system_prompt, prompt
