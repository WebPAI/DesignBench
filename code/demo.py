#%%
from runner.main import Runner
from utils import Framework, Task, Mode

# Initialize the Runner with a selected model and framework
runner = Runner(
    "gemini-2.0-flash",  # Name of the model to use (see mllm/__init__.py)
    framework=Framework.ANGULAR,  # Input framework (e.g., Angular source data)
    stream=True,  # Enable streaming output for stability (default: True)
    print_content=True,  # Print model outputs to console (default: False)
)

runner.run(
    task=Task.GENERATION,  # Choose from: GENERATION, EDIT, REPAIR, COMPULE
    output_framework=Framework.REACT,  # Must match the input framework for EDIT, REPAIR, and COMPULE tasks
    mode=Mode.IMAGE,  # Operation mode: IMAGE, CODE, BOTH, or MARK (see supported mode)
    max_workers=20,  # Number of threads for parallel execution
    execution_range=(1, 2),  # Optional: specify execution indices
)

#%%

from evaluator.main import *
from evaluator.compile import *
models = [
    "claude-3-7-sonnet-20250219",
    "gpt-4o-2024-11-20",
    "gemini-2.0-flash",
    "Llama-3.2-90B-Vision-Instruct",
    "Llama-3.2-11B-Vision-Instruct",
    "pixtral-large-latest",
    "pixtral-12b-2409",
    "qwen2.5-vl-72b-instruct",
    "qwen2.5-vl-7b-instruct"
] # Evaluated MLLMs

frame_works = ["react", "vue", "angular", "vanilla"] # the framework used to actually implement the webpage.
implemented_frame_works = ["react", "vue", "angular", "vanilla"] # the framework used by the MLLMs.

# collect the compile information
for frame_work in frame_works:
    if frame_work == "vanilla":
        continue
    for implemented in implemented_frame_works:
        collect_compile_information(task_name=Task.GENERATION, frame_work=frame_work, implemented_framework_or_mode=implemented)

evaluate_generation(models=models, frame_works=frame_works, implemented_frameworks=implemented_frame_works)

#%%

from evaluator.main import *
from evaluator.compile import *
models = [
    "claude-3-7-sonnet-20250219",
    "gpt-4o-2024-11-20",
    "gemini-2.0-flash",
    "Llama-3.2-90B-Vision-Instruct",
    "Llama-3.2-11B-Vision-Instruct",
    "pixtral-large-latest",
    "pixtral-12b-2409",
    "qwen2.5-vl-72b-instruct",
    "qwen2.5-vl-7b-instruct"
]

frame_works = ["react", "vue", "angular", "vanilla"]  # the framework used to actually implement the webpage.
modes = ["both", "code", "image"] # code, image, both
# collect the compile information
for frame_work in frame_works:
    if frame_work == "vanilla":
        continue
    for mode in modes:
        collect_compile_information(task_name=Task.EDIT, frame_work=frame_work, implemented_framework_or_mode=mode)

evaluate_generation(models=models, frame_works=frame_works, implemented_frameworks=implemented_frame_works)
evaluate_edit(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=False)
evaluate_edit(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=True)


#%%

from evaluator.main import *
from evaluator.compile import *
models = [
    "claude-3-7-sonnet-20250219",
    "gpt-4o-2024-11-20",
    "gemini-2.0-flash",
    "Llama-3.2-90B-Vision-Instruct",
    "Llama-3.2-11B-Vision-Instruct",
    "pixtral-large-latest",
    "pixtral-12b-2409",
    "qwen2.5-vl-72b-instruct",
    "qwen2.5-vl-7b-instruct"
]

frame_works = ["react", "vue", "angular", "vanilla"]  # the framework used to actually implement the webpage.
modes = ["both", "code", "image"]  # code, image, both
# collect the compile information
for frame_work in frame_works:
    if frame_work == "vanilla":
        continue
    for mode in modes:
        collect_compile_information(task_name=Task.REPAIR, frame_work=frame_work, implemented_framework_or_mode=mode)
evaluate_repair(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=False)
evaluate_repair(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=True)

