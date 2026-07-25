import difflib
import json
import os
import cv2
from PIL import Image
import torch
from selenium.webdriver.support.wait import WebDriverWait
from torch.nn.functional import cosine_similarity
import numpy as np
import clip
from nltk.translate.bleu_score import sentence_bleu
import easyocr
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm
import subprocess
import re
import base64
import time
from sklearn.metrics import jaccard_score
import urllib

# from ..prompting import mllm_utils

# DesignBench_Path = "/home/xjy/DesignBench/"

DesignBench_Path = "/Users/whalexiao/Downloads/pythonProject/UIEdit/DesignBench/"


# folder_dic = {
#     "generation": "../../data/DesignGeneration/",
#     "edit": "../../data/DesignEdit-3/",
#     "repair": "../../data/DesignRepair/",
# }

folder_dic = {
    "generation": "/dev/shm/data/DesignGeneration/",
    "edit": "../../data/DesignEdit/",
    # "edit": "/dev/shm/data/DesignEdit/",
    # "repair": "/dev/shm/data/DesignRepair/",
    "repair": "../../data/DesignRepair/",
    # "compile": "../../data/Compile/",
    "compile": "/Users/whalexiao/Desktop/WebPAIResults/DesignBenchResults/",
}

deploy_link_dic = {
    "vue": "http://localhost:5173/",  # npm run dev
    "react": "http://localhost:3000/",  # npm run dev
    "angular": "http://localhost:4200/",  # ng serve
}

project_code_path_dic = {
    "vue": DesignBench_Path + "web/my-vue-app/src/components/HelloWorld.vue",
    "react": DesignBench_Path + "web/my-react-app/app/page.tsx",
    "angular": DesignBench_Path + "web/my-angular-app/src/app/new.component.html"
    # "angular": {
    #     "html": DesignBench_Path + "web/my-angular-app/app/new.component.html",
    #     "ts": DesignBench_Path + "web/my-angular-app/app/new.component.ts"
    # }
}

format_dic = {
    "vue": "vue",
    "react": "jsx",
    "vanilla": "html",
    "angular": "angular"
}


# def save_html(link, filename):
#     # filename = f"{new_folder_path}/{image_index}.html"
#     os.system(f"npx single-file {link} {filename}")
#     # html_code = urllib.request.urlopen(link).read()
#     # with open(filename, "w") as fs:
#     #     fs.write(html_code)


single_path = "./single_file/single-file-cli-master/single-file"
def save_html(link, filename):
    # filename = f"{new_folder_path}/{image_index}.html"
    os.system(f"{single_path} {link} {filename}")

def run_angular_app(app_path=DesignBench_Path + "web/my-angular-app/", file_name="angular.png"):
    """
    运行Angular应用并收集错误信息

    参数:
        app_path: Angular应用的路径
        log_file: 日志文件名，如果为None则自动生成

    返回:
        (日志文件的路径, 编译是否成功)
    """
    # 如果没有指定日志文件，创建一个带时间戳的日志文件
    # if log_file is None:
    #     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #     log_file = f"angular_errors_{timestamp}.log"

    log_file = file_name.replace(".png", ".log")

    # 确保应用路径存在
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用路径 '{app_path}'")
        return None, False

    # print(f"启动 Angular 应用: {app_path}")
    # print(f"错误日志将保存至: {log_file}")

    # 编译状态标志
    compilation_success = True
    # compilation_complete = False

    try:
        # 打开日志文件
        with open(log_file, 'w', encoding='utf-8') as f:

            # 运行ng serve命令，并实时捕获输出
            process = subprocess.Popen(
                ['ng', 'serve', "--host", "0.0.0.0"],
                cwd=app_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            try:
                for line in process.stdout:
                    # 写入所有输出到日志
                    f.write(line)
                    f.flush()

                    # if "http://10.103.69.227:4200/" in line:
                    if deploy_link_dic["angular"] in line:
                        compilation_success = True
                        print("success")

                        web_driver = WebDriver(browser_name='firefox', url=deploy_link_dic["angular"], file=None,
                                               string=None,
                                               headless=True)

                        WebDriverWait(web_driver.driver, 30).until(
                            lambda d: d.execute_script('return document.readyState') == 'complete'
                        )
                        time.sleep(2)
                        # save_path = generated_code_path.replace(".html", ".png")
                        web_driver.take_screenshot(filename=file_name)
                        web_driver.quit()
                        save_html(link=deploy_link_dic["angular"], filename=file_name.replace(".png", ".html"))
                        process.kill()
                        return True
                        # exit(1)
                        # continue

                    if "ERROR" in line:
                        compilation_success = False
                        print("ERROR")

                    if "Watch mode enabled" in line:
                        if not compilation_success:
                            process.kill()
                            return False

            except KeyboardInterrupt:
                # 处理用户中断
                process.terminate()
                print("\n用户手动停止了应用")

            # if compilation_success:
            #     process.wait()
            # else:
            #     process.kill()
            # return log_file, compilation_success

    except Exception as e:
        print(f"运行过程中发生错误: {e}")
        return None, False


def git_diff_lines(file1, file2):
    result = subprocess.run(
        ["git", "diff", "--no-index", "--stat", "--unified=0", file1, file2],
        capture_output=True, text=True
    )
    print(result.stdout)


def code_similarity(src_code, reference_code, generated_code):
    # src_code = src_code.split("\n")
    # reference_code = reference_code.split("\n")

    # diff = difflib.unified_diff(src_code, reference_code)

    with open("code1", "w") as fs:
        fs.write(src_code)

    with open("code2", "w") as fs:
        fs.write(reference_code)

    with open("code3", "w") as fs:
        fs.write(generated_code)

    # git_diff_lines(file1="code1", file2="code2")
    #
    # git_diff_lines(file1="code1", file2="code3")

    line_numbers_ref, modified_code_ref = diff_files(file1_path="code1", file2_path="code2")

    line_numbers_generated, modified_code_generated = diff_files(file1_path="code1", file2_path="code3")

    line_numbers_ref = set(line_numbers_ref)
    line_numbers_generated = set(line_numbers_generated)

    print(line_numbers_ref)
    print(line_numbers_generated)
    print(line_numbers_ref.intersection(line_numbers_generated))

    interaction_line_numbers = line_numbers_ref.intersection(line_numbers_generated)
    #
    union_line_numbers = line_numbers_ref.union(line_numbers_generated)

    if len(union_line_numbers) == 0:
        return 1
        # if len() == 0:
        #     return 1
        # else:
        #     return 0
    else:
        jaccard = len(interaction_line_numbers) / len(union_line_numbers)
        return jaccard

    # return jaccard(line_numbers_ref, line_numbers_generated)

    # print(diff)
    # print(src_code)
    # print(reference_code)




def mae_score(img1, img2):
    """mean absolute error, it is a pixel-based metric"""
    img1, img2 = process_imgs(img1, img2, 512)
    # max_mae = np.mean(np.maximum(img1, 255 - img1))
    mae = np.mean(np.abs(img1 - img2))
    # return {"mae": mae, "normalized_mae": 1 - mae / max_mae}
    return mae


def process_imgs(image1, image2, max_size):
    # Get the original sizes
    width1, height1 = image1.size
    width2, height2 = image2.size

    # Determine the new dimensions (max of both images' width and height)
    new_width = max(width1, width2)
    new_height = max(height1, height2)

    # Pad images to the new dimensions with random values
    def pad_image(image, new_width, new_height):
        # Create a random padded background with the new dimensions
        random_padding = np.random.randint(0, 256, (new_height, new_width, 3), dtype=np.uint8)
        padded_image = Image.fromarray(random_padding)

        # Paste the original image onto the padded background (placing in the top-left corner)
        padded_image.paste(image, (0, 0))

        return padded_image

    padded_image1 = pad_image(image1, new_width, new_height)
    padded_image2 = pad_image(image2, new_width, new_height)

    # Calculate the aspect ratio for resizing to the max size
    aspect_ratio = min(max_size / new_width, max_size / new_height)
    new_size = (int(new_width * aspect_ratio), int(new_height * aspect_ratio))

    # Resize the padded images to the specified max size
    resized_image1 = padded_image1.resize(new_size, Image.LANCZOS)
    resized_image2 = padded_image2.resize(new_size, Image.LANCZOS)

    # resized_image1.show()
    # resized_image2.show()

    # Convert the images to numpy arrays with dtype int16
    array1 = np.array(resized_image1).astype(np.int16)
    array2 = np.array(resized_image2).astype(np.int16)

    return array1, array2




def ssim_similarity(image_path1, image_path2):
    image1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)
    image2_resized = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    score, diff = ssim(image1, image2_resized, full=True)
    return score



def render_ui(code_path, save_path, frame_work):
    # ToDo: input the generated code file path (e.g., /DesignEdit/1/result/1-gemini.html),
    #  save the screenshot of the image (e.g., /DesignEdit/1/result/1-gemini.png)

    print(code_path)
    if frame_work == "vanilla":
        print("render vanilla")
        try:
            web_driver = WebDriver(browser_name='firefox', url=None, file=code_path, string=None, headless=True)
            web_driver.take_screenshot(filename=save_path)
            web_driver.quit()
        except Exception as e:
            print(e)
            pass
        finally:
            return True
    else:
        return render_framework_ui(generated_code_path=code_path,
                                   project_code_path=project_code_path_dic[frame_work],
                                   deployed_link=deploy_link_dic[frame_work],
                                   save_path=save_path)




# encoding image for gemini
def gemini_encode_image(image_path):
    return Image.open(image_path)


# encoding image for gpt, claude, qwen, mistral, llama
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



def render_framework_ui(generated_code_path, project_code_path, deployed_link, save_path):
    # print(project_code_path)
    with open(generated_code_path, "r") as f_code:
        generated_code = f_code.read()
    with open(project_code_path, "w") as f_code:
        f_code.write(generated_code)

    # for angular app, write the ts file
    if "my-angular-app" in project_code_path:
        with open(generated_code_path.replace(".angular", ".ts"), "r") as f_ts:
            # print(generated_code_path.replace(".angular", ".ts"))
            generated_code = f_ts.read()
        with open(project_code_path.replace(".html", ".ts"), "w") as f_ts:
            # print(project_code_path.replace(".html", ".ts"))
            f_ts.write(generated_code)

        return run_angular_app(file_name=save_path)

    time.sleep(2)
    web_driver = WebDriver(browser_name='firefox', url=deployed_link, file=None, string=None, headless=True)

    WebDriverWait(web_driver.driver, 30).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    time.sleep(2)
    # save_path = generated_code_path.replace(".html", ".png")
    web_driver.take_screenshot(filename=save_path)
    web_driver.quit()
    save_html(link=deployed_link, filename=save_path.replace(".png", ".html"))

    return True





def get_compile_metric(web_name, model_name, framework, mode):
    # generated_path = prediction_path + f"{web_name}/result/{model_name}.png"

    generated_code_path = prediction_path + f"CompileResults/{framework}-{framework}/{model_name}/{framework}_{web_name}_{model_name}_{framework}_{mode}.{format_dic[framework]}"

    generated_img_path = generated_code_path.replace(f".{format_dic[framework]}", ".png")
    generated_html_path = generated_code_path.replace(f".{format_dic[framework]}", ".html")


    if re_calculate:
        if os.path.exists(generated_img_path):
            os.remove(generated_img_path)
        if os.path.exists(generated_html_path) and framework != "vanilla":
            os.remove(generated_html_path)

    if not os.path.exists(generated_img_path) or not os.path.exists(generated_html_path):
        # render
        compile_flag = render_ui(code_path=generated_code_path, save_path=generated_img_path, frame_work=framework)

        if not compile_flag:
            metrics = {
                "MAE": 0,
                "clip_similarity": 0,
                # "text_similarity": bleu_score,
                "structure_similarity": 0,
                # "layout_similarity": layout_score,
                # "position_similarity": ps_similarity,
                # "block_match": block_match_ratio,
            }
            return metrics



    config_file = prediction_path + f"{framework}/{web_name}/{web_name}.json"

    # with open(config_file, "r") as fs:
    #     config = json.loads(fs.read())
    #
    #     # original_img_path = prediction_path + f"{web_name}/.png"
    #     reference_img_path = prediction_path + f"{framework}/{web_name}/repaired.png"
    #     reference_code_path = prediction_path + f"{framework}/{web_name}/repaired.{format_dic[framework]}"
    #
    #
    #     # src_code = remove_comments(config["src_code"])
    #     # reference_code = remove_comments(config["dst_code"])
    #
    #     if framework == "react":
    #         src_code = config["component_jsx"]
    #     else:
    #         src_code = config["code"]
    #
    #     with open(reference_code_path, "r") as f_code:
    #         reference_code = f_code.read()
    #
    #     with open(generated_code_path, "r") as f_code:
    #         # generated_code = remove_comments(f_code.read())
    #         generated_code = f_code.read()

        # if framework == "angular":
        #     src_angular_code = src_code["html"]
        #     # reference_angular_code = reference_code["html"]
        #     reference_angular_code = reference_code
        #     angular_code_score = code_similarity(src_code=src_angular_code, reference_code=reference_angular_code,
        #                                  generated_code=generated_code)
        #     print("angular score:", angular_code_score)
        #     src_ts_code = src_code["ts"]
        #     # reference_ts_code = reference_code["ts"]
        #
        #     with open(reference_code_path.replace(".angular", ".ts"), "r") as f_code:
        #         reference_ts_code = f_code.read()
        #
        #     with open(generated_code_path.replace(".angular", ".ts"), "r") as f_code:
        #         # generated_code = remove_comments(f_code.read())
        #         generated_code = f_code.read()
        #
        #     ts_code_score = code_similarity(src_code=src_ts_code, reference_code=reference_ts_code,
        #                                  generated_code=generated_code)
        #
        #     print("ts score:", ts_code_score)
        #     code_score = 0.5 * angular_code_score + 0.5*ts_code_score
        # else:
        #     if framework == "react":
        #         src_code = remove_comments(src_code)
        #         reference_code = remove_comments(reference_code)
        #         generated_code = remove_comments(generated_code)
        #
        #     code_score = code_similarity(src_code=src_code, reference_code=reference_code, generated_code=generated_code)

        # reference_img = Image.open(reference_img_path)
        #
        # generated_img = Image.open(generated_img_path)
        #
        # mae = mae_score(img1=reference_img, img2=generated_img)
        # cp_score = clip_similarity(reference_img_path, generated_img_path)
        # # bleu_score = get_bleu(reference_image=reference_img, generated_image=generated_img)
        # ssim_score = ssim_similarity(reference_img_path, generated_img_path)


    metrics = {

        "MAE": 0,
        "clip_similarity": 0,
        # "text_similarity": bleu_score,
        "structure_similarity": 0,
        "code_score": 0,
        # "code_similarity": code_score,
        # "layout_similarity": layout_score,
        # "position_similarity": ps_similarity,
        # "block_match": block_match_ratio,
        # "llm judge": llm_score
    }
    return metrics



def evaluate_compile(models, frame_works, modes):

    for frame_work in frame_works:
        begin, end = 0, 0
        if frame_work == "angular":
            begin, end = 1, 10
        if frame_work == "react":
            begin, end = 1, 10

        if frame_work == "vue":
            begin, end = 1, 10

        if frame_work == "vanilla":
            # begin, end = 1, 80
            begin, end = 1, 28

        for model_name in models:
            for mode in modes:
                results = {}
                res_path = f"./res/DesignCompile/{frame_work}_{mode}.json"
                if os.path.exists(res_path):
                    with open(res_path, "r") as fs:
                        results = json.loads(fs.read())
                # if model_name not in results:
                #     results[model_name] = {}
                # else:
                #     results[model_name] = {}

                if model_name not in results:
                    results[model_name] = {}

                for i in tqdm(range(begin, end + 1)):
                    metric = get_compile_metric(web_name=str(i), model_name=model_name, framework=frame_work, mode=mode)
                    results[model_name][str(i)] = metric
                    print(metric)
                with open(res_path, "w") as fs:
                    fs.write(json.dumps(results))


if __name__ == "__main__":
    # web_name = 1
    # edit_name = 1
    # model_name = "gemini"
    # model_name = "pixtral"
    # prompt_name = "direct_prompt"
    # prediction_path = "../../data/DesignEdit/"
    # prediction_path = "../../data/DesignGeneration/"

    task = "compile"
    prediction_path = folder_dic[task]

    re_calculate = False

    models = [
        # "claude-sonnet-4-6",
        # "gpt-5.4-2026-03-05",
        # "gemini-3.1-pro-preview",
        # "claude-sonnet-4-20250514",
        # "gpt-5",
        # "gemini-2.5-pro",
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

    # frame_works = ["vue"]
    # frame_works = ["react", "vue", "vanilla"]
    # frame_works = ["vue"]
    # modes = ["both", "code", "image"]
    frame_works = ["react", "vue", "angular"]
    # modes = ["mark", "both", "code", "image"]
    modes = ["both"]
    # modes = ["mark", "both", "code", "image"]



    # modes = ["mark"]
    # modes = ["mark"]
    # modes = ["image"]
    # modes = ["both"]
    # modes = ["image"]

    evaluate_compile(models=models, frame_works=frame_works, modes=modes)