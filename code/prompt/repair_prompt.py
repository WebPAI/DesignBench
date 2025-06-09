from typing import Tuple, Union, Dict
from utils import Framework, Mode

REPAIR_GENERIC_SYSTEM_PROMPT_TEMPLATE = """
{introduction}
You are proficient in UI repair.
You take a screenshot, a piece of code of a reference web page with design issues{extra_info}.
You need to repair the UI display issues.

Here are the issue types and explanations:

- occlusion: Elements are hidden or partially covered by other elements, making content inaccessible or invisible to users. This includes overlapping components, modal dialogs blocking content, or elements positioned behind others.
- crowding: Too many elements are packed into a small space without adequate spacing, making the interface feel cluttered and difficult to navigate. This affects readability and user experience.
- text overlap: Text content overlaps with other text or UI elements, making it unreadable or causing visual confusion. This often occurs due to improper positioning, z-index issues, or responsive design problems.
- alignment: Elements are not properly aligned with each other or the overall layout grid, creating a disorganized and unprofessional appearance. This includes misaligned text, buttons, images, or containers.
- color and contrast: Poor color choices that affect readability or accessibility, including insufficient contrast between text and background, or color combinations that are difficult for users with visual impairments to distinguish.
- overflow: Content extends beyond its intended container boundaries, causing horizontal scrollbars, cut-off text, or elements appearing outside their designated areas.

Requirements:
- Do not modify the code except for the part with display issues.
- For images, use placeholder images from https://placehold.co
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.


Output Format:

Please provide the following information and output them using the tags: [ISSUES] ... [/ISSUES] , [REASONING] ... [/REASONING], and [CODE] ... [/CODE].

1. Display issues: occlusion/crowding/text overlap/alignment/color and contrast/overflow, you should output all the issues in a list [].

2. Reasoning:
   - Explain your rationale about the display issues.
   - Describe specific elements that involving design issues

3. Repaired Code: The complete fixed code

{output_format}

Do not output any extra information or comments.
"""


VANILLA_OUTPUT_FORMAT = """
You MUST wrap your entire code output inside the following markdown fences: ```html and ```.

Please follow the format of the example response below:

[ISSUES]
["text overlap"]
[/ISSUES]

[REASONING]
The main heading text overlaps with the navigation menu due to absolute positioning without proper z-index management. The h1 element with 'position: absolute; top: 16px; left: 16px' is positioned behind the navigation bar, making the title partially unreadable. Additionally, the navigation items are too close together without proper spacing, causing readability issues on smaller screens.
[/REASONING]

[CODE]
```html
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Header Component</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        .header {{
            position: relative;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        .nav {{
            background-color: #2563eb;
            color: white;
            padding: 12px 16px;
            position: relative;
            z-index: 10;
        }}
        
        .nav ul {{
            display: flex;
            list-style: none;
            gap: 24px;
        }}
        
        .nav a {{
            color: white;
            text-decoration: none;
        }}
        
        .nav a:hover {{
            text-decoration: underline;
        }}
        
        .title-section {{
            padding: 32px 16px;
        }}
        
        .title {{
            font-size: 1.875rem;
            font-weight: bold;
            color: #1f2937;
            position: relative;
            z-index: 0;
        }}
    </style>
</head>
<body>
    <header class=\"header\">
        <nav class=\"nav\">
            <ul>
                <li><a href=\"#\">Home</a></li>
                <li><a href=\"#\">About</a></li>
                <li><a href=\"#\">Services</a></li>
                <li><a href=\"#\">Contact</a></li>
            </ul>
        </nav>
        <div class=\"title-section\">
            <h1 class=\"title\">Welcome to Our Website</h1>
        </div>
    </header>
</body>
</html>
```
[/CODE]
"""


REACT_OUTPUT_FORMAT = """
You MUST wrap your entire code output inside the following markdown fences: ```jsx and ```.

Please follow the EXTAC format of the example response below:
[ISSUES]
["text overlap"]
[/ISSUES]

[REASONING]
The main heading text overlaps with the navigation menu due to absolute positioning without proper z-index management. The h1 element with 'absolute top-4 left-4' is positioned behind the navigation bar, making the title partially unreadable. Additionally, the navigation items are too close together without proper spacing, causing readability issues on smaller screens.
[/REASONING]

[CODE]
```jsx
import React from 'react';

function Header() {{
  return (
    <header className=\"relative bg-white shadow-sm\">
      <nav className=\"bg-blue-600 text-white px-4 py-3 relative z-10\">
        <ul className=\"flex space-x-6\">
          <li><a href=\"#\" className=\"hover:underline\">Home</a></li>
          <li><a href=\"#\" className=\"hover:underline\">About</a></li>
          <li><a href=\"#\" className=\"hover:underline\">Services</a></li>
          <li><a href=\"#\" className=\"hover:underline\">Contact</a></li>
        </ul>
      </nav>
      <div className=\"px-4 py-8\">
        <h1 className=\"text-3xl font-bold text-gray-800 relative z-0\">
          Welcome to Our Website
        </h1>
      </div>
    </header>
  );
}}

export default Header;"
}}
```
[/CODE]
"""


VUE_OUTPUT_FORMAT = """
You MUST wrap your entire code output inside the following markdown fences: ```vue and ```.

Please follow the format of the example response below:
[ISSUES]
["text overlap"]
[/ISSUES]

[REASONING]
The main heading text overlaps with the navigation menu due to absolute positioning without proper z-index management. The h1 element with 'absolute top-4 left-4' is positioned behind the navigation bar, making the title partially unreadable. Additionally, the navigation items are too close together without proper spacing, causing readability issues on smaller screens.
[/REASONING]

[CODE]
```vue
<template>
  <header class=\"relative bg-white shadow-sm\">
    <nav class=\"bg-blue-600 text-white px-4 py-3 relative z-10\">
      <ul class=\"flex space-x-6\">
        <li><a href=\"#\" class=\"hover:underline\">Home</a></li>
        <li><a href=\"#\" class=\"hover:underline\">About</a></li>
        <li><a href=\"#\" class=\"hover:underline\">Services</a></li>
        <li><a href=\"#\" class=\"hover:underline\">Contact</a></li>
      </ul>
    </nav>
    <div class=\"px-4 py-8\">
      <h1 class=\"text-3xl font-bold text-gray-800 relative z-0\">
        Welcome to Our Website
      </h1>
    </div>
  </header>
</template>

<script>
export default {{
  name: 'HeaderComponent'
}}
</script>

<style scoped>
/* Additional styles if needed */
</style>"
}}
```
[/CODE]
"""


ANGULAR_OUTPUT_FORMAT = """
You MUST wrap your HTML template file inside the following markdown fences: ```angular and ```;
You MUST wrap your TypeScript component file inside the following markdown fences: ```ts and ```.

Please follow the format of the example response below:
[ISSUES]
["text overlap"]
[/ISSUES]

[REASONING]
The main heading text overlaps with the navigation menu due to absolute positioning without proper z-index management. The h1 element with 'absolute top-4 left-4' is positioned behind the navigation bar, making the title partially unreadable. Additionally, the navigation items are too close together without proper spacing, causing readability issues on smaller screens.
[/REASONING]

[CODE]
```angular
<header class=\"relative bg-white shadow-sm\">
  <nav class=\"bg-blue-600 text-white px-4 py-3 relative z-10\">
    <ul class=\"flex space-x-6\">
      <li><a href=\"#\" class=\"hover:underline\">Home</a></li>
      <li><a href=\"#\" class=\"hover:underline\">About</a></li>
      <li><a href=\"#\" class=\"hover:underline\">Services</a></li>
      <li><a href=\"#\" class=\"hover:underline\">Contact</a></li>
    </ul>
  </nav>
  <div class=\"px-4 py-8\">
    <h1 class=\"text-3xl font-bold text-gray-800 relative z-0\">
      Welcome to Our Website
    </h1>
  </div>
</header>
```
and
```ts
import { Component } from '@angular/core';
@Component({
  selector: 'app-header',
  templateUrl: './new.component.html',
  styleUrls: ['./new.component.css']
})
export class NewComponent {
  constructor() { }
}
```
[/CODE]
"""


def get_design_repair_prompt(output_framework: Framework, mode: Mode, code: Union[str, Dict]) -> Tuple[str, str]:
    
    # ========== Design Repair System Prompt ==========
    extra_info = ", the design issues are are marked by red bounding boxes" if mode == Mode.MARK else ""
    
    if output_framework == Framework.VANILLA:
        introduction = "You are an expert HTML/CSS developer."
        output_format = VANILLA_OUTPUT_FORMAT.strip()
    elif output_framework == Framework.REACT:
        introduction = "You are an expert React/Tailwind developer."
        output_format = REACT_OUTPUT_FORMAT.strip()
    elif output_framework == Framework.VUE:
        introduction = "You are an expert Vue/Tailwind developer."
        output_format = VUE_OUTPUT_FORMAT.strip()
    elif output_framework == Framework.ANGULAR:
        introduction = "You are an expert Angular/Tailwind developer."
        output_format = ANGULAR_OUTPUT_FORMAT.strip()
    else:
        raise ValueError(f"Unsupported framework: {output_framework.value}")
    
    system_prompt = REPAIR_GENERIC_SYSTEM_PROMPT_TEMPLATE.format(
        introduction=introduction,
        extra_info=extra_info,
        output_format=output_format
    ).strip()
    
    
    # ========== Design Repair Prompt ==========
    if output_framework == Framework.ANGULAR:
        ts_code = code["ts"]
        html_code = code["html"]
        code_message = f"The Angular HTML code:\n```angular\n{html_code}\n```\nThe TypeScript code:\n```ts\n{ts_code}\n```"
    else:
        code_message = f"The code is {code}."
    
    image_message = "The screenshot:"
    
    if mode == Mode.CODE:
        prompt = code_message
    elif mode == Mode.IMAGE:
        prompt = image_message
    elif mode in [Mode.BOTH, Mode.MARK]:
        prompt = f"{code_message} {image_message}"
    else:
        raise ValueError(f"Unsupported mode: {mode.value}")

    return system_prompt, prompt
    