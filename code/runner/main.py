import os
import json
from typing import Tuple, Optional, List, Union, Dict
from tqdm.auto import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from mllm import get_model
from utils import Framework, Task, Mode, extract_code_snippet, extract_repair_content
from prompt import get_design_generation_prompt, get_design_edit_prompt, get_design_repair_prompt, get_design_compile_repair_prompt

def get_begin_end(framework: Framework, task: Task) -> range:
    # (framework, task): (begin, end)
    task_ranges = {
        (Framework.VANILLA, Task.GENERATION): (1, 120),
        (Framework.REACT, Task.GENERATION): (1, 109),
        (Framework.VUE, Task.GENERATION): (1, 118),
        (Framework.ANGULAR, Task.GENERATION): (1, 83),
        
        (Framework.VANILLA, Task.EDIT): (1, 80),
        (Framework.REACT, Task.EDIT): (1, 108),
        (Framework.VUE, Task.EDIT): (1, 105),
        (Framework.ANGULAR, Task.EDIT): (1, 66),
        
        (Framework.VANILLA, Task.REPAIR): (1, 28),
        (Framework.REACT, Task.REPAIR): (1, 28),
        (Framework.VUE, Task.REPAIR): (1, 27),
        (Framework.ANGULAR, Task.REPAIR): (1, 28),
        
        (Framework.VANILLA, Task.COMPILE): (1, 10),
        (Framework.REACT, Task.COMPILE): (1, 10),
        (Framework.VUE, Task.COMPILE): (1, 10),
        (Framework.ANGULAR, Task.COMPILE): (1, 10),
    }

    try:
        begin, end = task_ranges[(framework, task)]
    except KeyError:
        raise ValueError(f"Invalid combination: {framework.value} {task.value}")
    
    return range(begin, end + 1)


class Runner:
    def __init__(self, model_name: str, framework: Framework, stream: bool = True, print_content: bool = False, **kwargs) -> None:
        self.folder_dic = {
            Task.GENERATION: f"data/generation/{framework.value}/",
            Task.EDIT: f"data/edit/{framework.value}/",
            Task.REPAIR: f"data/repair/{framework.value}/",
            Task.COMPILE: f"data/compile/{framework.value}/",
        }
        self.model_name = model_name
        self.model_filename = model_name.split("/")[-1]
        self.model = get_model(self.model_name, **kwargs)
        self.framework = framework
        self.stream = stream
        self.print_content = print_content
    
    def get_output_formats(self, output_framework: Framework) -> Tuple[str, ...]:
        if output_framework == Framework.VANILLA:
            return ["html"]
        elif output_framework == Framework.REACT:
            return ["jsx"]
        elif output_framework == Framework.VUE:
            return ["vue"]
        elif output_framework == Framework.ANGULAR:
            return ["ts", "angular"]
        else:
            raise ValueError(f"Unsupported framework: {output_framework.value}")
    
    def save_files(self, save_dir: str, save_name: str, contents: List[str], output_formats: List[str]) -> None:
        os.makedirs(save_dir, exist_ok=True)
        for content, fmt in zip(contents, output_formats):
            save_path = os.path.join(save_dir, f"{save_name}.{fmt}")
            with open(save_path, "w") as f:
                f.write(content)
    
    def check_files_exist(self, save_dir: str, save_name: str, output_formats: List[str]) -> bool:
        os.makedirs(save_dir, exist_ok=True)
        return all(os.path.exists(os.path.join(save_dir, f"{save_name}.{fmt}")) for fmt in output_formats)
    
    def run(self, task: Task, output_framework: Framework, mode: Mode, max_workers: int = 20, execution_range: Optional[Tuple[int, int]] = None, stop_if_error: bool = False) -> int:
        execution_range = range(*execution_range) if execution_range else get_begin_end(self.framework, task)
        
        if task in [Task.EDIT, Task.REPAIR, Task.COMPILE] and self.framework != output_framework:
            raise ValueError(f"Framework mismatch: {self.framework.value} vs {output_framework.value}")
        
        if task == Task.GENERATION:
            execution_function = self.run_generation
        elif task == Task.EDIT:
            execution_function = self.run_edit
        elif task == Task.REPAIR:
            execution_function = self.run_repair
        elif task == Task.COMPILE:
            execution_function = self.run_compile_error_repair
        else:
            raise ValueError(f"Unsupported task: {task.value}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            execution_tasks = [(task, str(i), output_framework, mode) for i in execution_range]
            futures = {executor.submit(execution_function, t): t[1] for t in execution_tasks}
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"{self.model_name}: Running {task.value} ({self.framework.value} -> {output_framework.value} / {mode.value})"):
                web_number = futures[future]
                if stop_if_error:
                    future.result()
                else:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error in {task.value} for {web_number}: {e}")
    
    def run_generation(self, args: Tuple) -> int:
        task, web_number, output_framework, mode = args
        output_formats = self.get_output_formats(output_framework)
        
        if mode != Mode.IMAGE:
            raise ValueError("mode should be 'image' for generation task")
        
        save_dir = f"results/{task.value}/{self.framework.value}-{output_framework.value}/{self.model_filename}/"
        save_name = f"{self.framework.value}_{web_number}_{self.model_filename}_{output_framework.value}"
        if self.check_files_exist(save_dir=save_dir, save_name=save_name, output_formats=output_formats):
            return web_number

        image_path = self.folder_dic[task] + f"{web_number}/{web_number}.png"
        
        def generation_exec(image_path: str, output_framework: Framework, output_formats: List[str]) -> Tuple[str, Tuple[str, ...]]:
            images = [self.model.encode_image(image_path)]
            system_prompt, prompt = get_design_generation_prompt(output_framework=output_framework)
            response = self.model.chat(system_prompt=system_prompt, prompt=prompt, images=images, stream=self.stream, print_content=self.print_content)
            code_snippets = extract_code_snippet(response, output_framework=output_framework)
            return response, code_snippets

        response, code_snippets = generation_exec(
            image_path=image_path,
            output_framework=output_framework,
            output_formats=output_formats
        )
        
        self.save_files(save_dir=save_dir, save_name=save_name, contents=code_snippets, output_formats=output_formats)
        with open(save_dir + f"{save_name}.txt", "w") as fs:
            fs.write(response)
        return web_number

    def run_edit(self, args: Tuple) -> int:
        task, web_number, output_framework, mode = args
        output_formats = self.get_output_formats(output_framework)
        
        if mode not in [Mode.CODE, Mode.IMAGE, Mode.BOTH]:
            raise ValueError("mode should be 'code', 'image', or 'both'")
        
        with open(self.folder_dic[task] + f"{web_number}/{web_number}.json", "r") as f_config:
            config = json.loads(f_config.read())
            prompt, src_id, src_code = config["prompt"], config["src_id"], config["src_code"]
            src_image_path = self.folder_dic[task] + f"{web_number}/{src_id}.png"
        
        
        save_dir = f"results/{task.value}/{self.framework.value}-{output_framework.value}/{self.model_filename}/"
        save_name = f"{self.framework.value}_{web_number}_{self.model_filename}_{output_framework.value}_{mode.value}"
        if self.check_files_exist(save_dir=save_dir, save_name=save_name, output_formats=output_formats):
            return web_number
        
        def edit_exec(output_framework: Framework, mode: Mode, instruction: str, image_path: str, code: Union[str, Dict]) -> Tuple[str, Tuple[str, ...]]:
            images = [self.model.encode_image(image_path)]
            system_prompt, prompt = get_design_edit_prompt(framework=output_framework, mode=mode, instruction=instruction, code=code)
            if mode == Mode.CODE:
                response = self.model.chat(system_prompt=system_prompt, prompt=prompt, stream=self.stream, print_content=self.print_content)
            elif mode in [Mode.IMAGE, Mode.BOTH]:  
                response = self.model.chat(system_prompt=system_prompt, prompt=prompt, images=images, stream=self.stream, print_content=self.print_content)
            
            code_snippets = extract_code_snippet(response, output_framework=output_framework)
            return response, code_snippets

        response, code_snippets = edit_exec(
            output_framework=output_framework,
            mode=mode,
            instruction=prompt,
            image_path=src_image_path,
            code=src_code
        )
        
        self.save_files(save_dir=save_dir, save_name=save_name, contents=code_snippets, output_formats=output_formats)
        with open(save_dir + f"{save_name}.txt", "w") as fs:
            fs.write(response)
        return web_number
    
    def run_repair(self, args: Tuple) -> int:
        task, web_number, output_framework, mode = args
        output_formats = self.get_output_formats(output_framework)
        
        if mode not in [Mode.CODE, Mode.IMAGE, Mode.BOTH, Mode.MARK]:
            raise ValueError("mode should be 'code', 'image', 'both', or 'mark'")
        
        config_path = self.folder_dic[task] + f"{web_number}/{web_number}.json"
        with open(config_path, "r") as f_config:
            config = json.loads(f_config.read())
            code = config["component_jsx"] if self.framework == Framework.REACT else config["code"]
        
        original_image_path = self.folder_dic[task] + f"{web_number}/{web_number}.png"
        marked_image_path = self.folder_dic[task] + f"{web_number}/{web_number}_mark.png"
        save_dir = f"results/{task.value}/{self.framework.value}-{output_framework.value}/{self.model_filename}/"
        save_name = f"{self.framework.value}_{web_number}_{self.model_filename}_{output_framework.value}_{mode.value}"
        if self.check_files_exist(save_dir=save_dir, save_name=save_name, output_formats=output_formats):
            return web_number
        
        def repair_exec(output_framework: Framework, mode: Mode, code: Union[str, Dict], original_image_path: str, marked_image_path: str, output_formats: List[str]) -> Tuple[str, dict]:
            original_images = [self.model.encode_image(original_image_path)]
            marked_images = [self.model.encode_image(marked_image_path)]
            system_prompt, prompt = get_design_repair_prompt(output_framework=output_framework, mode=mode, code=code)
            
            if mode == Mode.CODE:
                response = self.model.chat(system_prompt=system_prompt, prompt=prompt, stream=self.stream, print_content=self.print_content)
            elif mode in [Mode.IMAGE, Mode.BOTH]:
                response = self.model.chat(system_prompt=system_prompt, prompt=prompt, images=original_images, stream=self.stream, print_content=self.print_content)
            elif mode == Mode.MARK:
                response = self.model.chat(system_prompt=system_prompt, prompt=prompt, images=marked_images, stream=self.stream, print_content=self.print_content)
            
            issues, reasoning, code = extract_repair_content(response, output_framework=output_framework)
            code = {"ts": code[0], "html": code[1]} if output_framework == Framework.ANGULAR else code
            cleanup_json = {
                "Issues": issues,
                "Reasoning": reasoning,
                "Code": code,
            }
            return response, cleanup_json
        
        response, cleanup_json = repair_exec(
            output_framework=output_framework,
            mode=mode,
            code=code,
            original_image_path=original_image_path,
            marked_image_path=marked_image_path,
            output_formats=output_formats,
        )

        code_snippets = [cleanup_json["Code"]] if isinstance(cleanup_json["Code"], str) else list(cleanup_json["Code"])
        self.save_files(save_dir=save_dir, save_name=save_name, contents=code_snippets, output_formats=output_formats)
        with open(save_dir + f"{save_name}.json", "w") as fs:
            json.dump(cleanup_json, fs, indent=4)
        with open(save_dir + f"{save_name}.txt", "w") as fs:
            fs.write(response)
        
        return web_number
    
    def run_compile_error_repair(self, args: Tuple) -> int:
        task, web_number, output_framework, mode = args
        output_formats = self.get_output_formats(output_framework)
        
        if mode not in [Mode.CODE, Mode.BOTH]:
            raise ValueError("mode should be 'code' or 'both'")
        
        config_path = self.folder_dic[task] + f"{web_number}/{web_number}.json"
        with open(config_path, "r") as f_config:
            config = json.loads(f_config.read())
            error_info = config["issue"]
            code = config["code"]
        
        save_dir = f"results/{task.value}/{self.framework.value}-{output_framework.value}/{self.model_filename}/"
        save_name = f"{self.framework.value}_{web_number}_{self.model_filename}_{output_framework.value}_{mode.value}"
        if self.check_files_exist(save_dir=save_dir, save_name=save_name, output_formats=output_formats):
            return web_number
        
        def compile_error_repair_exec(output_framework: Framework, mode: Mode, code: Union[str, Dict], error_info: str) -> Tuple[str, dict]:
            system_prompt, prompt = get_design_compile_repair_prompt(framework=output_framework, mode=mode, code=code, error_info=error_info)
            response = self.model.chat(system_prompt=system_prompt, prompt=prompt, stream=self.stream, print_content=self.print_content)
            code_snippets = extract_code_snippet(response, output_framework=output_framework)
            return response, code_snippets
        
        response, code_snippets = compile_error_repair_exec(
            output_framework=output_framework,
            mode=mode,
            code=code,
            error_info=error_info
        )

        self.save_files(save_dir=save_dir, save_name=save_name, contents=code_snippets, output_formats=output_formats)
        with open(save_dir + f"{save_name}.txt", "w") as fs:
            fs.write(response)
        return web_number