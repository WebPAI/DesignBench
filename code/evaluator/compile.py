import re
import os
import json
import tqdm
from PIL import Image
import numpy as np
from config import *


def is_pure_white_image(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)
        return np.all(img_array == [255, 255, 255])
    except Exception:
        return False


def check_html_png(html_or_log_path, error_type):
    html_or_log_path = html_or_log_path.strip('"')

    if not os.path.isfile(html_or_log_path):
        return "NULL"

    if error_type == "angular":
        html_path = os.path.splitext(html_or_log_path)[0] + '.html'
        if os.path.isfile(html_path):
            return "NULL"

        try:
            with open(html_or_log_path, 'r', encoding='utf-8') as file:
                log_content = file.read()
                print(log_content)
        except Exception:
            return "NULL"

        # pattern = r'(?:TS|NG)-?\d{4,}(?:-\d+)?'
        pattern = r".*\[plugin angular-compiler\].*"
        error_codes = re.findall(pattern, log_content)
        return error_codes[0] if error_codes else "no html"

    if not os.path.isfile(html_or_log_path):
        return "NULL"

    try:
        with open(html_or_log_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except Exception:
        return "NULL"

    if error_type == "vue":
        pattern = r'</span><span class=message-body part=message-body>(.*?)</span>'
    elif error_type == "react":
        pattern = r'style=color:var\(--color-ansi-truecolor\)>\×</span><span>(.*?)╭─\[</span>'
    else:
        return "NULL"

    match = re.search(pattern, html_content, re.DOTALL)

    if match:
        return match.group(1)
    else:
        png_path = os.path.splitext(html_or_log_path)[0] + '.png'
        if os.path.isfile(png_path) and is_pure_white_image(png_path):
            return "blank"
        else:
            return "NULL"


def batch_process(json_path, base_folder, error_type):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Cannot read JSON file {json_path}: {e}")
        return

    for model_name in tqdm.tqdm(data):
        model_folder = os.path.join(base_folder, model_name)
        if not os.path.isdir(model_folder):
            print(f"Model folder {model_folder} does not exist, skipping {model_name}")
            continue

        for seq in data[model_name]:
            seq_pattern = f'_{seq}_'
            target_file = None
            extension = '.log' if error_type == 'angular' else '.html'

            for file in os.listdir(model_folder):
                if file.endswith(extension) and seq_pattern in file:
                    target_file = os.path.join(model_folder, file)
                    break

            if not target_file:
                # print(f"Model {model_name} Number {seq} cannot find the corresponding {extension} file")
                data[model_name][seq]['compile_error'] = "NULL"
                continue

            result = check_html_png(target_file, error_type)
            # print(f"Model {model_name}，Number {seq}，File {target_file}，Result:{result}")

            data[model_name][seq]['compile_error'] = result

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"JSON file：{json_path} is updated successfully!")
    except Exception as e:
        print(f"Cannot save JSON file {json_path}: {e}")


def collect_compile_information(task_name, frame_work, implemented_framework_or_mode):
    json_path = ""
    base_folder = ""

    if task_name == Task.GENERATION:
        json_path = f"./res/DesignGeneration/{frame_work}_{implemented_framework_or_mode}.json"
        base_folder = DesignBench_Path + f"data/DesignRepair/GenerationResults/{frame_work}-{implemented_framework_or_mode}"

    if task_name == Task.EDIT:
        json_path = f"./res/DesignEdit/{frame_work}_{implemented_framework_or_mode}.json"
        base_folder = DesignBench_Path + f"data/DesignRepair/EditResults/{frame_work}-{frame_work}"


    if task_name == Task.REPAIR:
        json_path = f"./res/DesignRepair/{frame_work}_{implemented_framework_or_mode}.json"
        base_folder = DesignBench_Path + f"data/DesignRepair/RepairResults/{frame_work}-{frame_work}"


    # if not os.path.isfile(json_path):
    #     print(f"JSON file {json_path} not found")
    #     return
    # if not os.path.isdir(base_folder):
    #     print(f"Folder {base_folder} not found")
    #     return
    #
    # while True:
    #     error_type = input("please input the type of the error html (vue, react, or angular): ").lower().strip()
    #     if error_type in ["vue", "react", "angular"]:
    #         break
    #     print("input invalid，please input 'vue'、'react' or 'angular'")

    batch_process(json_path, base_folder, error_type=frame_work)


if __name__ == "__main__":
    # frame_works = ["angular", "react", "vue", "vanilla"]
    # implemented_frameworks = ["angular", "react", "vue"]

    # frame_works = ["vanilla"]
    # implemented_frameworks = ["react"]
    # frame_works = ["angular", "react", "vue", "vanilla"]
    # implemented_frameworks = ["angular", "react", "vue"]

    # frame_works = ["angular", "react", "vue"]
    # frame_works = ["react", "vue"]

    frame_works = ["react", "vue"]

    implemented_frameworks = ["mark", "both", "code", "image"]

    # implemented_frameworks = ["both"]
    for frame_work in frame_works:
        for implemented in implemented_frameworks:
            collect_compile_information(task_name=Task.REPAIR, frame_work=frame_work, implemented_framework_or_mode=implemented)



