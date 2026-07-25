import json
import numpy as np
import pandas as pd
import re
import tiktoken
#
# delete_dic = {
#     "angular": [6, 38],
#     "react": [24],
#     "vue": [],
#     "vanilla": []
# }


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    使用tiktoken计算文本的token数量

    Args:
        text (str): 要计算的文本
        model (str): 模型名称，默认为gpt-3.5-turbo

    Returns:
        int: token数量
    """
    try:
        encoder = tiktoken.encoding_for_model(model)
        tokens = encoder.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0


def calculate_prompt_length_label():
    frames = ["vanilla", "vue", "angular", "react"]
    for frame_work in frames:
        begin, end = 0, 0
        if frame_work == "angular":
            begin, end = 1, 66
        if frame_work == "react":
            begin, end = 1, 108

        if frame_work == "vue":
            begin, end = 1, 105

        if frame_work == "vanilla":
            begin, end = 1, 80
        hard = 0
        easy = 0
        medium = 0
        for web_name in range(begin, end + 1):
            json_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.json"
            with open(json_file, "r") as fs:
                data = json.loads(fs.read())
                diff = data["difficulty"]
                text = data["prompt"]

                token_number = count_tokens(text)
                if token_number > 40:
                    hard += 1
                    data["length"] = "hard"
                elif token_number < 30:
                    easy += 1
                    data["length"] = "easy"
                else:
                    medium += 1
                    data["length"] = "medium"
            with open(json_file, "w") as fs:
                fs.write(json.dumps(data, indent=4))

                # if diff == "hard":
                #     hard += 1
                # if diff == "easy":
                #     easy += 1
                # if diff == "medium":
                #     medium += 1
            # pass
        #     png_file = f"../../../data/DesignGeneration/{frame_work}/{web_name}/{web_name}.png"
        #     json_file = f"../../../data/DesignGeneration/{frame_work}/{web_name}/{web_name}.json"
        #
        #     with open(json_file, "r") as fs:
        #         data = json.loads(fs.read())
        #         w = data["image width"]
        #         h = data["image height"]
        #         # print(w, h)
        #         if h > 2000:
        #             data["size"] = "hard"
        #             hard += 1
        #         elif h < 1000:
        #             data["size"] = "easy"
        #             easy += 1
        #         else:
        #             data["size"] = "medium"
        #             medium += 1
        #     with open(json_file, "w") as fs:
        #         fs.write(json.dumps(data, indent=4))
        print(frame_work, easy, medium, hard)


def extract_score(text):
    pattern = r'"score":\s*(\d+)'  # 匹配"score": 后面的数字
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    return None


def get_difficulty_for_design_edit(web_name, frame):
    with open(f"{data_dir}/{frame}/{web_name}/{web_name}.json", "r") as fs:
        data = json.loads(fs.read())

    return data["difficulty"]
    # return data["length"]

def get_difficulty_for_design_repair(web_name, frame):
    with open(f"{data_dir}/{frame}/{web_name}/{web_name}.json", "r") as fs:
        data = json.loads(fs.read())

    return data["modified"]


def get_res(file_name, frame):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {

    }
    models = [
        # "claude-3-7-sonnet-20250219",
        # "gpt-4o-2024-11-20",
        "gemini-2.0-flash",
        # "Llama-3.2-90B-Vision-Instruct",
        # "Llama-3.2-11B-Vision-Instruct",
        # "pixtral-large-latest",
        # "pixtral-12b-2409",
        # "qwen2.5-vl-72b-instruct",
        # "qwen2.5-vl-7b-instruct"
        # "qwen2.5-vl-3b-instruct",
    ]
    for model in data.keys():
        res[model] = {}
        for difficulty in ["easy", "medium", "hard"]:
            res[model][difficulty] = []
        # print(model)
        for web_name in data[model].keys():
            # metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
            #           data[model][web_name]["text_similarity"], data[model][web_name]["structure_similarity"],
            #           data[model][web_name]["layout_similarity"]]
            # print(web_name, model)
            # if int(web_name) in delete_dic[frame]:
            #     continue
            try:
                llm_score = data[model][web_name]["llm score"]
                llm_score = extract_score(llm_score)
            except:
                llm_score = 0
            # print(llm_score[7:-3])
            # llm_score = json.loads(llm_score[7:-3])

            # difficulty = get_difficulty(web_name=web_name, frame=frame)
            if task == "DesignRepair":
                difficulty = get_difficulty_for_design_repair(web_name=web_name, frame=frame)
            else:
                difficulty = get_difficulty_for_design_edit(web_name=web_name, frame=frame)

            # print(difficulty)

            if "compile_error" in data[model][web_name] and data[model][web_name]["compile_error"] == "NULL" or (
                    frame == "vanilla"):
                metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                          data[model][web_name]["structure_similarity"], data[model][web_name]["code_score"], llm_score,
                          1]
            else:
                metric = [0, 0, 0, 0, 0, 0]

            # metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
            #           data[model][web_name]["structure_similarity"], llm_score]

            # if difficulty == "hard":
            # if model in models:
            #     print(web_name, metric, difficulty)

            res[model][difficulty].append(metric)
        for difficulty in ["easy", "medium", "hard"]:
            res[model][difficulty] = np.array(res[model][difficulty])
            res[model][difficulty][res[model][difficulty] == None] = 1
            res[model][difficulty] = list(np.mean(np.array(res[model][difficulty]), axis=0))

        # res[model][res[model] == None] = 0

    # 将字典转换为DataFrame
    # df = pd.DataFrame.from_dict(res, orient='index', columns=['MAE', 'CLIP', 'Text', 'SSIM', "Layout"])

    df = pd.DataFrame.from_dict({(i, j): res[i][j]
                                 for i in res.keys()
                                 for j in res[i].keys()},
                                orient='index', columns=['MAE', 'CLIP', "SSIM", "Code", "LLM Score", "Compile"])

    #
    # df = pd.DataFrame.from_dict({(i, j): res[i][j]
    #                         for i in res.keys()
    #                         for j in res[i].keys()},
    #                        orient='index', columns=[ 'MAE', 'CLIP', "SSIM", "LLM Score"])

    # df = pd.DataFrame.from_dict(res, orient='index', columns=['Difficulty', 'MAE', 'CLIP', "SSIM", "Code", "LLM Score"])
    df.index.name = 'model_name'
    df = df.round(4)
    df = df.round(4)

    # 显示所有列
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 1000)

    pd.set_option('display.width', 5000)

    # 保存为CSV文件
    # df.to_csv('./results/output_vanilla.csv')
    # print(file_name)
    # print(df)
    # print(df["LLM Score"])
    # === 修改：不再返回带 MultiIndex 的 Series，直接返回原来的扁平数组，
    #     同时把模型名顺序（res.keys() 的顺序，即 df 里 model 分组的顺序）一并返回，
    #     方便最后 reshape 成 Model Name, Easy, Medium, Hard 的表格。 ===
    return np.array(df["LLM Score"]), list(res.keys())
    # === 修改结束 ===
    # return np.array(df["Code"])
    # print(json.dumps(res, indent=4))



def get_metric_by_difficulty():
    frames = ["angular", "vanilla", "react", "vue"]
    # frames = ["angular"]
    # modes = ["both"]
    modes = ["both"]

    res = []
    model_names = None  # === 修改：记录模型名顺序，用于最后 reshape 成表格 ===
    for frame in frames:
        for mode in modes:
            scores, models_this_frame = get_res(file_name=f"{res_dir}/{frame}_{mode}.json", frame=frame)
            res.append(scores)
            # print(scores)
            if model_names is None:  # 修改：用第一个 frame 的模型顺序作为基准
                model_names = models_this_frame

    mean_scores = np.round(np.mean(np.array(res), axis=0), 4)
    # print(mean_scores)

    # === 修改：mean_scores 是按 模型顺序 + [easy, medium, hard] 顺序拍平的一维数组，
    #     直接 reshape 成 (模型数, 3)，配合 model_names 做成 Model Name, Easy, Medium, Hard 的表格。 ===
    table = pd.DataFrame(mean_scores.reshape(-1, 3), columns=["Easy", "Medium", "Hard"])
    table.insert(0, "Model Name", model_names)

    print("\nFinal LLM Score averaged across frames (angular/vanilla/react/vue):")
    print(table.to_string(index=False))
    # === 修改结束 ===

    pass



task = "DesignEdit"
data_dir = "/Users/whalexiao/Downloads/pythonProject/UIEdit/DesignBench/data/DesignEdit"
res_dir = "./res/DesignEdit"

print(task)
get_metric_by_difficulty()

task = "DesignRepair"
data_dir = "/Users/whalexiao/Downloads/pythonProject/UIEdit/DesignBench/data/DesignRepair"
res_dir = "./res/DesignRepair"
print(task)
get_metric_by_difficulty()