import json
import numpy as np

import pandas as pd


def get_compile_result(file_name):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {

    }

    for model in data.keys():
        res[model] = []
        for web_name in data[model].keys():
            if "compile_error" in data[model][web_name] and data[model][web_name]["compile_error"] == "NULL" or ("vanilla" in file_name):
            # if True:
                metric = [1]
            else:
                metric = [0]
            res[model].append(metric)
        res[model] = np.array(res[model])
        res[model][res[model] == None] = 1.0
        res[model] = list(np.mean(np.array(res[model]), axis=0))


    df = pd.DataFrame.from_dict(res, orient='index', columns=["Compile"])
    df.index.name = 'model_name'

    df = df.round(4)
    # 显示所有列
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 1000)

    pd.set_option('display.width', 5000)

    print(file_name)

    print(df)
    #
    # # key = "Code"
    # # key = "Compile"
    # # key = "LLM Score"
    # key = "Issue Accuracy"
    # print(df)
    #
    # # res = " & ".join(map(str, list(df[key])))
    #
    # res = " & ".join([f"{x:.4f}" for x in list(df[key])])
    #
    # # res = " & ".join([f"{x:.2%}" for x in df[key]])
    # print("& " + res + " \\" + "\\")
    #
    # print(df[key].mean())

def get_compile_metric():
    frames = ["vue", "angular", "react"]
    # frames = ["angular"]
    # modes = ["both"]
    modes = ["both"]

    res = []
    for frame in frames:
        for mode in modes:
            scores = get_compile_result(file_name=f"./res/DesignCompile/{frame}_{mode}.json")
            res.append(scores)
            print(scores)



get_compile_metric()




