import json
import os
import shutil
import re
import numpy as np
import pandas as pd
import tiktoken

format_dic = {
    "react": "jsx",
    "vue": "vue",
    "angular": "angular"
}


def get_res(file_name):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {

    }
    for model in data.keys():
        res[model] = []
        for web_name in data[model].keys():
            # metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
            #           data[model][web_name]["text_similarity"], data[model][web_name]["structure_similarity"],
            #           data[model][web_name]["layout_similarity"]]
            if "compile_error" not in data[model][web_name] or data[model][web_name]["compile_error"] == "NULL":
                metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                          data[model][web_name]["structure_similarity"], 1]
            else:
                # metric = [0, 0, 0, 0]
                # metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                #           data[model][web_name]["structure_similarity"], 0]
                metric = [0, 0, 0, 0]
                # if "claude" in model and ("Unexpected EOF in tag" in data[model][web_name]["compile_error"] or
                #                           "Unexpected token" in data[model][web_name]["compile_error"]
                #                             or "Element is missing end tag." in data[model][web_name]["compile_error"]):
                #
                # # if "claude" in model:
                #     metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                #               data[model][web_name]["structure_similarity"], 1]

            res[model].append(metric)
        res[model] = np.array(res[model])

        res[model][res[model] == None] = 1.0
        res[model] = list(np.mean(np.array(res[model]), axis=0))

    # 将字典转换为DataFrame
    # df = pd.DataFrame.from_dict(res, orient='index', columns=['MAE', 'CLIP', 'Text', 'SSIM', "Layout"])
    df = pd.DataFrame.from_dict(res, orient='index', columns=['MAE', 'CLIP', "SSIM", "Compile"])
    df.index.name = 'model_name'

    df = df.round(4)

    # 保存为CSV文件
    # df.to_csv('./results/output_vanilla.csv')
    print(file_name)
    # print(df)
    # key = "Compile"
    key = "CLIP"
    print(df[key])

    # res = " & ".join(map(str, list(df[key])))
    res = " & ".join([f"{x:.4f}" for x in list(df[key])])

    # res = " & ".join([f"{x:.2%}" for x in df[key]])

    print("& " + res + " \\" + "\\")

    print(df[key].mean())


def extract_score(text):
    pattern = r'"score":\s*(\d+)'  # 匹配"score": 后面的数字
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    return None


def get_edit_res(file_name):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {

    }
    models = ["claude-3-7-sonnet-20250219",
              "gpt-4o-2024-11-20",
              "gemini-2.0-flash",
              "Llama-3.2-90B-Vision-Instruct",
              "Llama-3.2-11B-Vision-Instruct",
              "pixtral-large-latest",
              "pixtral-12b-2409",
              "qwen2.5-vl-72b-instruct",
              "qwen2.5-vl-7b-instruct"
              ]
    #
    # for model in data.keys():

    for model in models:
        res[model] = []
        for web_name in data[model].keys():
            # metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
            #           data[model][web_name]["text_similarity"], data[model][web_name]["structure_similarity"],
            #           data[model][web_name]["layout_similarity"]]
            # print(web_name, model)
            try:
                llm_score = data[model][web_name]["llm score"]
                llm_score = extract_score(llm_score)
            except:
                llm_score = 0

            if "compile_error" in data[model][web_name] and data[model][web_name]["compile_error"] == "NULL" or (
                    "vanilla" in file_name):
                metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                          data[model][web_name]["structure_similarity"], data[model][web_name]["code_score"], llm_score,
                          1]
            else:
                metric = [0, 0, 0, 0, 0, 0]
            res[model].append(metric)
        res[model] = np.array(res[model])
        res[model][res[model] == None] = 1.0
        res[model] = list(np.mean(np.array(res[model]), axis=0))

    # 将字典转换为DataFrame
    # df = pd.DataFrame.from_dict(res, orient='index', columns=['MAE', 'CLIP', 'Text', 'SSIM', "Layout"])
    df = pd.DataFrame.from_dict(res, orient='index', columns=['MAE', 'CLIP', "SSIM", "Code", "LLM Score", "Compile"])
    df.index.name = 'model_name'
    df = df.round(4)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 1000)

    pd.set_option('display.width', 5000)

    # 保存为CSV文件
    # df.to_csv('./results/output_vanilla.csv')
    print(file_name)
    # print(df)

    key = "LLM Score"
    # key = "Code"
    # key = "Compile"
    # print(df[key])

    # res = " & ".join(map(str, list(df[key])))

    res = " & ".join([f"{x:.4f}" for x in list(df[key])])

    # res = " & ".join([f"{x:.2%}" for x in df[key]])
    # print("& " + res + " \\" + "\\")
    #
    # print("& CSR & " + res + " \\" + "\\")
    #
    # print(df[key].mean())
    return np.array(df[key])


def get_edit_result_context():
    # frames = ["react", "vue", "angular", "vanilla"]
    # modes = ["both"]

    frames = ["react", "vue", "angular", "vanilla"]
    # modes = ["both", "code", "image"]
    modes = ["image", "code", "both"]

    final = []
    for mode in modes:
        res = []
        for frame in frames:
            scores = get_edit_res(file_name=f"{res_dir}/{frame}_{mode}.json")
            res.append(scores)
        res = np.array(res)
        res = np.mean(res, axis=0)
        res = np.round(res, 4)
        print(res)
        final.append(res)

    print(np.array(final).T)

    # for frame in frames:
    #     for mode in modes:
    #         get_edit_res(file_name=f"./designedit/{frame}_{mode}.json")
    # res.append(scores)
    # print(scores)
    # print("-----------------------------------------------")


def get_repair_result(file_name):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {

    }

    for model in data.keys():
        res[model] = []
        for web_name in data[model].keys():
            # metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
            #           data[model][web_name]["text_similarity"], data[model][web_name]["structure_similarity"],
            #           data[model][web_name]["layout_similarity"]]
            # print(web_name, model)
            try:
                llm_score = data[model][web_name]["llm score"]
                llm_score = extract_score(llm_score)
            except:
                llm_score = 0
            # print(llm_score[7:-3])
            # llm_score = json.loads(llm_score[7:-3])

            if "compile_error" in data[model][web_name] and data[model][web_name]["compile_error"] == "NULL" or (
                    "vanilla" in file_name):
                # if True:
                metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                          data[model][web_name]["structure_similarity"], data[model][web_name]["code_score"],
                          data[model][web_name]["issue accuracy"], llm_score, 1]
            else:
                metric = [0, 0, 0, 0, 0, 0, 0]
            res[model].append(metric)
        res[model] = np.array(res[model])
        res[model][res[model] == None] = 1.0
        res[model] = list(np.mean(np.array(res[model]), axis=0))

    df = pd.DataFrame.from_dict(res, orient='index',
                                columns=['MAE', 'CLIP', "SSIM", "Code", "Issue Accuracy", "LLM Score", "Compile"])
    df.index.name = 'model_name'

    df = df.round(4)
    # 显示所有列
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 1000)

    pd.set_option('display.width', 5000)

    # print(file_name)
    # print(df)

    # key = "Code"
    # key = "Compile"
    key = "LLM Score"
    # key = "Issue Accuracy"
    # print(df)

    # res = " & ".join(map(str, list(df[key])))

    # res = " & ".join([f"{x:.4f}" for x in list(df[key])])
    #
    # # res = " & ".join([f"{x:.2%}" for x in df[key]])
    # print("& " + res + " \\" + "\\")
    #
    # print(df[key].mean())
    return df[key]


def get_repair_metric_context():

    frames = ["react", "vue", "angular", "vanilla"]
    # modes = ["both", "code", "image"]
    modes = ["code", "image"]
    # modes = ["image", "code", "both", "mark"]

    final = []
    for mode in modes:
        res = []
        for frame in frames:
            scores = get_repair_result(file_name=f"{res_dir}/{frame}_{mode}.json")
            res.append(scores)
        res = np.array(res)
        res = np.mean(res, axis=0)
        res = np.round(res, 4)
        print(res)
        final.append(res)

    print(np.array(final).T)

    # res = []
    # for frame in frames:
    #     for mode in modes:
    #         scores = get_repair_result(file_name=f"./designrepair/{frame}_{mode}.json")
    #         res.append(scores)
    #         print(scores)


res_dir = "./res/DesignRepair"
get_repair_metric_context()
