import re
import json
from typing import Optional, Tuple, List

from .format import Framework


def modify_angular_component(code: str) -> str:
    substitutions = [
        # 1. Change the class name to NewComponent
        (r'(export\s+class\s+)\w+Component\b', r'\1NewComponent'),
        
        # 2. Change the selector to 'app-new'
        (r'(selector\s*:\s*)(["\'])(.*?)(\2)', r"\1'app-new'"),
        
        # 3. Change templateUrl to './new.component.html'
        (r'(templateUrl\s*:\s*)(["\'])(.*?)(\2)', r"\1'./new.component.html'"),
        
        # 4. Change styleUrls to ['./new.component.css']
        (r'(styleUrls\s*:\s*)\[[^\]]*\]', r"\1['./new.component.css']"),
    ]

    for pattern, repl in substitutions:
        code = re.sub(pattern, repl, code, flags=re.MULTILINE)

    # 5. Add ngOnInit implementation if class is empty
    code = re.sub(
        r'export class (\w+) implements OnInit \{\s*\}',
        r'export class \1 implements OnInit {\n\n  ngOnInit(): void {\n    \n  }\n}',
        code
    )

    return code


def extract_code_block(content: str, languages: List[str]) -> str:
    for lang in languages:
        marker = f"```{lang}"
        if marker in content:
            return content.split(marker)[-1].split("```")[0].strip()
    return ""


def extract_code_snippet(content: str, output_framework: Framework) -> Tuple[str, ...]:
    if output_framework == Framework.VANILLA:
        return (extract_code_block(content, ["html"]),)
    elif output_framework == Framework.REACT:
        return (extract_code_block(content, ["jsx", "react", "javascript"]),)
    elif output_framework == Framework.VUE:
        return (extract_code_block(content, ["vue", "javascript"]),)
    elif output_framework == Framework.ANGULAR:
        ts_code = extract_code_block(content, ["ts", "typescript"])
        ts_code = modify_angular_component(ts_code)
        html_code = extract_code_block(content, ["angular", "html"])
        return ts_code, html_code


def extract_repair_content(content: str, output_framework: Framework) -> Tuple[List[str], str, Optional[str | Tuple[str, str]]]:
    issues, reasoning, code = "", "", ""
    if "[ISSUES]" in content and "[/ISSUES]" in content:
        try:
            issues = json.loads(content.split("[ISSUES]")[-1].split("[/ISSUES]")[0].strip())
        except json.JSONDecodeError:
            issues = []
    if "[REASONING]" in content and "[/REASONING]" in content:
        reasoning = content.split("[REASONING]")[-1].split("[/REASONING]")[0].strip()
    if "[CODE]" in content and ("[/CODE]" in content or "```" in content):
        code = content.split("[CODE]")[-1].split("[/CODE]")[0].strip()
        code = extract_code_snippet(code, output_framework)
    return issues, reasoning, code