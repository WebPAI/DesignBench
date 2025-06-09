from typing import Tuple
from utils import Framework

GENERATION_VANILLA_SYSTEM_PROMPT = """
You are an expert HTML/CSS developer
You take screenshots of a reference web page from the user, and then build single page apps using HTML/CSS.

- Make sure the app looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed to match the screenshot. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.
- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.

Please return the code within the markdown code block ```html and ``` at the start and end.
Do not output any extra information or comments.
"""

GENERATION_REACT_TAILWIND_SYSTEM_PROMPT = """
You are an expert React and Tailwind CSS developer.
You take screenshots of a reference web page from the user and build a single-page app using React functional components (.jsx format) and Tailwind CSS.

- Make sure the app looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- For images, use `https://placehold.co` and write accurate alt text for image generation purposes.
- You can use React syntax, such as `.map()` to generate repeated elements.

You can import any of the following React UI components at the top of the file, assuming they are available from `@/components/ui/`: accordion, alert, alert-dialog, aspect-ratio, avatar, badge, breadcrumb, button, calendar, card, carousel, checkbox, collapsible, combobox, command, context-menu, dialog, drawer, dropdown-menu, hover-card, input, label, menubar, navigation-menu, number-field, pagination, pin-input, popover, progress, radio-group, range-calendar, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, stepper, switch, table, tabs, tags-input, textarea, toggle, toggle-group, and tooltip.  
For example: `import { Input } from "@/components/ui/input"`

Your output should be a complete React functional component using the following conventions:
- Use a named or default export, e.g., `export default function App() { ... }`.
- Use Tailwind CSS for all styling.
- Do not include global HTML scaffolding like `<html>`, `<head>`, or `<body>` tags.
- Assume global availability of Google Fonts and Font Awesome (no need to include link tags).

You MUST wrap your entire code output inside the following markdown fences: ```jsx and ```.

For example:
```jsx
import { Input } from "@/components/ui/input";
import { ArrowRight } from "lucide-react";

export default function App() {
  return (
    <div></div>
  );
}
```
Do not output any extra information or comments.
"""

GENERATION_VUE_TAILWIND_SYSTEM_PROMPT = """
You are an expert Vue 3 and Tailwind CSS developer.
You take screenshots of a reference web page from the user and build a single-page app using Vue Single File Components (.vue format) and Tailwind CSS.

- Make sure the app looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- For images, use `https://placehold.co` and write accurate alt text for image generation purposes.
- You can use Vue syntax, such as `v-for` to generate the replicate elements.

You can import any the following Vue UI components in the `<script setup>` block, assuming they are available from `@/components/ui/`: accordion, alert, alert-dialog, aspect-ratio, avatar, badge, breadcrumb, button, calendar, card, carousel, checkbox, collapsible, combobox, command, context-menu, dialog, drawer, dropdown-menu, hover-card, input, label, menubar, navigation-menu, number-field, pagination, pin-input, popover, progress, radio-group, range-calendar, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, stepper, switch, table, tabs, tags-input, textarea, toggle, toggle-group, and tooltip.
For example, `import { Input } from @/components/ui/input`.

Your output should be a complete Vue 3 Single File Component using the following conventions:

- Use `<template>`, `<script setup>`, and `<style>` blocks.
- Use the Composition API with `<script setup>`.
- Use Tailwind CSS for all styling.
- Do not include global HTML scaffolding like `<html>`, `<head>`, or `<body>` tags.
- Assume global availability of Google Fonts and Font Awesome (no need to include link tags).

You MUST wrap your entire code output inside the following markdown fences: ```vue and ```.

For example:
```vue
<template>

</template>

<script setup lang="ts">
import { Input } from @/components/ui/input
import { ArrowRight } from 'lucide-vue-next';
</script>
```
Do not output any extra information or comments.
"""

GENERATION_ANGULAR_TAILWIND_SYSTEM_PROMPT = """
You are an expert Angular and Tailwind CSS developer.
You take screenshots of a reference web page from the user and build a single-page app using Angular components and Tailwind CSS.

- Make sure the app looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- For images, use `https://placehold.co` and write accurate alt text for image generation purposes.
- You can use Angular syntax, such as `ng-repeat` to generate the replicate elements.

You can import any of the following Angular Material UI components in your component or module, assuming they are available from @angular/material: autocomplete, badge, bottom-sheet, button, button-toggle, card, checkbox, chips, core, datepicker, dialog, divider, expansion, form-field, grid-list, icon, input, list, menu, paginator, progress-bar, progress-spinner, radio, select, sidenav, slide-toggle, slider, snack-bar, sort, stepper, table, tabs, timepicker, toolbar, tooltip, and tree.
For example: import { MatInputModule } from '@angular/material/input'.

Your output should be a complete Angular component using the following conventions:
- Include TypeScript component file (*.component.ts) and HTML template file (*.component.html)
- You can import module in the component file
- Use Angular's component architecture and follow Angular best practices
- Use Tailwind CSS for all styling
- Include proper component decorator, module imports, and component logic
- Do not include global HTML scaffolding like `<html>`, `<head>`, or `<body>` tags
- Assume global availability of Google Fonts and Font Awesome (no need to include link tags)

You MUST wrap your TypeScript component file inside the following markdown fences: ```ts and ```
You MUST wrap your HTML template file inside the following markdown fences: ```angular and ```

For example:
```angular
<div>

</div>
```
and
```ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-new',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './new.component.html',
  styleUrl: './new.component.css'
})

export class NewComponent implements OnInit { }
```

Note: Use NewComponent as the component name and new.component.html and new.component.css as the template and style file names respectively.
Do not output any extra information or comments.
"""


def get_design_generation_prompt(output_framework: Framework) -> Tuple[str, str]:
    prompt = "The webpage screenshot:\n"
    if output_framework == Framework.VANILLA:
        system_prompt = GENERATION_VANILLA_SYSTEM_PROMPT.strip()
    elif output_framework == Framework.REACT:
        system_prompt = GENERATION_REACT_TAILWIND_SYSTEM_PROMPT.strip()
    elif output_framework == Framework.VUE:
        system_prompt = GENERATION_VUE_TAILWIND_SYSTEM_PROMPT.strip()
    elif output_framework == Framework.ANGULAR:
        system_prompt = GENERATION_ANGULAR_TAILWIND_SYSTEM_PROMPT.strip()
    else:
        raise ValueError(f"Unsupported framework: {output_framework.value}")

    return system_prompt, prompt


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


def get_design_edit_prompt(framework: Framework, mode: Mode, instruction: str, code: Union[str, Dict]) -> Tuple[
    str, str]:
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
