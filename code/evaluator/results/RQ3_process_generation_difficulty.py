# import json
# import numpy as np
# from PIL import Image
# import pandas as pd
# from webpage_difficulty import cal_webpage_difficulty
#
#
# def calculate_difficulty_label():
#     frames = ["vanilla", "vue", "angular", "react"]
#     for frame_work in frames:
#         begin, end = 0, 0
#         if frame_work == "angular":
#             begin, end = 1, 83
#         if frame_work == "react":
#             begin, end = 1, 109
#
#         if frame_work == "vue":
#             begin, end = 1, 118
#
#         if frame_work == "vanilla":
#             begin, end = 1, 120
#         hard = 0
#         easy = 0
#         medium = 0
#         for web_name in range(begin, end + 1):
#             png_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.png"
#             html_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.html"
#             json_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.json"
#
#             with open(json_file, "r") as fs:
#                 data = json.loads(fs.read())
#
#                 score = cal_webpage_difficulty(png_file=png_file, html_file=html_file)
#                 print(score)
#
#                 if score > 75:
#                     data["difficulty"] = "hard"
#                     hard += 1
#                 elif score < 25:
#                     data["difficulty"] = "easy"
#                     easy += 1
#                 else:
#                     data["difficulty"] = "medium"
#                     medium += 1
#
#                 data["diff_score"] = score
#
#             with open(json_file, "w") as fs:
#                 fs.write(json.dumps(data, indent=4))
#         print(frame_work, easy, medium, hard)
#
#         # img = Image.open(png_file)
#         # imgSize = img.size  # 大小/尺寸
#         # w = img.width  # 图片的宽
#         # h = img.height
#         # with open(json_file, "r") as fs:
#         #     data = json.loads(fs.read())
#         # data["image width"] = w
#         # data["image height"] = h
#
#
# def get_difficulty(frame, web_name):
#     with open(f"{data_dir}/{frame}/{web_name}/{web_name}.json", "r") as fs:
#         data = json.loads(fs.read())
#
#     score = data["diff_score"]
#     if score > 80:
#         return "hard"
#     elif score < 30:
#         return "easy"
#     else:
#         return "medium"
#
#
# def get_generation_res_by_difficulty(file_name, src_frame, dst_frame):
#     # with open(f"results/res_vanilla_react.json", "r") as fs:
#     with open(file_name, "r") as fs:
#         data = json.loads(fs.read())
#
#     res = {}
#     total = 0
#     for model in data.keys():
#         print(model)
#         res[model] = {}
#         for diff in ["easy", "medium", "hard"]:
#             res[model][diff] = []
#
#         for web_name in data[model].keys():
#             difficulty = get_difficulty(src_frame, web_name)
#
#             if "compile_error" not in data[model][web_name] or data[model][web_name]["compile_error"] == "NULL":
#                 metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
#                           data[model][web_name]["structure_similarity"], 1]
#             else:
#                 # metric = [0, 0, 0, 0]
#                 metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
#                           data[model][web_name]["structure_similarity"], 0]
#
#             res[model][difficulty].append(metric)
#
#         for difficulty in ["easy", "medium", "hard"]:
#             # print(res[model][difficulty])
#             if res[model][difficulty] == []:
#                 res[model][difficulty] = [0, 0, 0, 0]
#             else:
#                 res[model][difficulty] = np.array(res[model][difficulty])
#                 res[model][difficulty][res[model][difficulty] == None] = 1
#                 res[model][difficulty] = list(np.mean(np.array(res[model][difficulty]), axis=0))
#
#     df = pd.DataFrame.from_dict({(i, j): res[i][j]
#                                  for i in res.keys()
#                                  for j in res[i].keys()},
#                                 orient='index', columns=['MAE', 'CLIP', "SSIM", "Compile"])
#
#     # df = pd.DataFrame.from_dict(res, orient='index', columns=['Difficulty', 'MAE', 'CLIP', "SSIM", "Code", "LLM Score"])
#     df.index.name = 'model_name'
#     df = df.round(4)
#
#     # 显示所有列
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.max_rows', None)
#     pd.set_option('max_colwidth', 1000)
#     pd.set_option('display.width', 5000)
#
#     # 保存为CSV文件
#     # df.to_csv('./results/output_vanilla.csv')
#     # print(df)
#
#     # return np.array(df["CLIP"])
#     return np.array(df["CLIP"])
#
#
# def get_difficulty_res():
#     src_frames = ["angular", "react", "vue", "vanilla"]
#     # dst_frames = ["angular", "react", "vue", "vanilla"]
#     dst_frames = ["react"]
#
#     # calculate_size_label()
#
#     res = []
#     for src_frame in src_frames:
#         for dst_frame in dst_frames:
#             dst_frame = src_frame
#             # print(src_frame, dst_frame)
#             clips = get_generation_res_by_difficulty(file_name=f"{res_dir}/{src_frame}_{dst_frame}.json",
#                                                      src_frame=src_frame,
#                                                      dst_frame=dst_frame)
#             res.append(clips)
#             # print(clips)
#             # print("-----------------------------------------------")
#
#     res = np.array(res)
#     res = np.mean(res, axis=0)
#     res = np.round(res, 4)
#
#     print(res)
#
#
#
# data_dir = "/Users/whalexiao/Downloads/pythonProject/UIEdit/DesignBench/data/DesignGeneration"
#
# res_dir = "../res_new/DesignGeneration"
#
# get_difficulty_res()


import json
import numpy as np
from PIL import Image
import pandas as pd
from webpage_difficulty import cal_webpage_difficulty


def calculate_difficulty_label():
    frames = ["vanilla", "vue", "angular", "react"]
    for frame_work in frames:
        begin, end = 0, 0
        if frame_work == "angular":
            begin, end = 1, 83
        if frame_work == "react":
            begin, end = 1, 109

        if frame_work == "vue":
            begin, end = 1, 118

        if frame_work == "vanilla":
            begin, end = 1, 120
        hard = 0
        easy = 0
        medium = 0
        for web_name in range(begin, end + 1):
            png_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.png"
            html_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.html"
            json_file = f"{data_dir}/{frame_work}/{web_name}/{web_name}.json"

            with open(json_file, "r") as fs:
                data = json.loads(fs.read())

                score = cal_webpage_difficulty(png_file=png_file, html_file=html_file)
                print(score)

                if score > 75:
                    data["difficulty"] = "hard"
                    hard += 1
                elif score < 25:
                    data["difficulty"] = "easy"
                    easy += 1
                else:
                    data["difficulty"] = "medium"
                    medium += 1

                data["diff_score"] = score

            with open(json_file, "w") as fs:
                fs.write(json.dumps(data, indent=4))
        print(frame_work, easy, medium, hard)

        # img = Image.open(png_file)
        # imgSize = img.size  # 大小/尺寸
        # w = img.width  # 图片的宽
        # h = img.height
        # with open(json_file, "r") as fs:
        #     data = json.loads(fs.read())
        # data["image width"] = w
        # data["image height"] = h


def get_difficulty(frame, web_name):
    with open(f"{data_dir}/{frame}/{web_name}/{web_name}.json", "r") as fs:
        data = json.loads(fs.read())

    score = data["diff_score"]
    if score > 80:
        return "hard"
    elif score < 30:
        return "easy"
    else:
        return "medium"


def get_generation_res_by_difficulty(file_name, src_frame, dst_frame):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {}
    total = 0
    for model in data.keys():
        print(model)
        res[model] = {}
        for diff in ["easy", "medium", "hard"]:
            res[model][diff] = []

        for web_name in data[model].keys():
            difficulty = get_difficulty(src_frame, web_name)

            if "compile_error" not in data[model][web_name] or data[model][web_name]["compile_error"] == "NULL":
                metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                          data[model][web_name]["structure_similarity"], 1]
            else:
                # metric = [0, 0, 0, 0]
                metric = [data[model][web_name]["MAE"], data[model][web_name]["clip_similarity"],
                          data[model][web_name]["structure_similarity"], 0]

            res[model][difficulty].append(metric)

        for difficulty in ["easy", "medium", "hard"]:
            # print(res[model][difficulty])
            if res[model][difficulty] == []:
                res[model][difficulty] = [0, 0, 0, 0]
            else:
                res[model][difficulty] = np.array(res[model][difficulty])
                res[model][difficulty][res[model][difficulty] == None] = 1
                res[model][difficulty] = list(np.mean(np.array(res[model][difficulty]), axis=0))

    df = pd.DataFrame.from_dict({(i, j): res[i][j]
                                 for i in res.keys()
                                 for j in res[i].keys()},
                                orient='index', columns=['MAE', 'CLIP', "SSIM", "Compile"])

    # df = pd.DataFrame.from_dict(res, orient='index', columns=['Difficulty', 'MAE', 'CLIP', "SSIM", "Code", "LLM Score"])
    df.index.name = 'model_name'
    df = df.round(4)

    # 显示所有列
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 1000)
    pd.set_option('display.width', 5000)

    # 保存为CSV文件
    # df.to_csv('./results/output_vanilla.csv')
    # print(df)

    # === 修改：改为输出 CLIP 指标，而不是每个难度级别的样本个数。
    #     res[model][difficulty] 是 [MAE, CLIP, SSIM, Compile]，CLIP 对应下标 1，
    #     按 model_name, easy, medium, hard 的形式整理成表格并打印出来。 ===
    clip_records = {
        model: {difficulty: res[model][difficulty][1] for difficulty in ["easy", "medium", "hard"]}
        for model in res.keys()
    }
    clip_df = pd.DataFrame.from_dict(clip_records, orient='index', columns=['easy', 'medium', 'hard'])
    clip_df.index.name = 'model_name'
    clip_df = clip_df.round(4).reset_index()

    print(f"\n[{src_frame} -> {dst_frame}] CLIP score by difficulty:")
    print(clip_df.to_string(index=False))
    # === 修改结束 ===

    # === 修改：把每个模型的 CLIP 指标表一并返回，方便调用方（如 get_difficulty_res）汇总或保存 ===
    return np.array(df["CLIP"]), clip_df
    # === 修改结束 ===


def get_difficulty_res():
    src_frames = ["angular", "react", "vue", "vanilla"]
    # dst_frames = ["angular", "react", "vue", "vanilla"]
    dst_frames = ["react"]

    # calculate_size_label()

    res = []
    # === 修改：收集每个 src_frame 对应的 CLIP 指标表，最后统一打印一份总览 ===
    all_clip_dfs = []
    # === 修改结束 ===
    for src_frame in src_frames:
        for dst_frame in dst_frames:
            dst_frame = src_frame
            # print(src_frame, dst_frame)
            # === 修改：get_generation_res_by_difficulty 现在返回 (clips, clip_df) ===
            clips, clip_df = get_generation_res_by_difficulty(file_name=f"{res_dir}/{src_frame}_{dst_frame}.json",
                                                     src_frame=src_frame,
                                                     dst_frame=dst_frame)
            clip_df.insert(0, "frame", src_frame)  # 修改：标记这份 CLIP 指标属于哪个 frame
            all_clip_dfs.append(clip_df)
            # === 修改结束 ===
            res.append(clips)
            # print(clips)
            # print("-----------------------------------------------")

    res = np.array(res)
    res = np.mean(res, axis=0)
    res = np.round(res, 4)

    print(res)

    # === 修改：打印所有 frame 汇总后的 model_name, easy, medium, hard 的 CLIP 指标表 ===
    if all_clip_dfs:
        all_clips = pd.concat(all_clip_dfs, ignore_index=True)
        print("\nAll frames CLIP score by difficulty:")
        print(all_clips.to_string(index=False))

        # === 修改：对 react/vue/angular/vanilla 四个 frame 求均值，
        #     得到每个模型在 easy/medium/hard 三个难度下、跨所有 frame 平均的 CLIP 分数 ===
        avg_clip_df = all_clips.groupby('model_name', as_index=False)[['easy', 'medium', 'hard']].mean().round(4)
        print("\nAverage CLIP score by difficulty across all frames (react/vue/angular/vanilla):")
        print(avg_clip_df.to_string(index=False))
        # === 修改结束 ===
    # === 修改结束 ===



data_dir = "/Users/whalexiao/Downloads/pythonProject/UIEdit/DesignBench/data/DesignGeneration"

res_dir = "./res/DesignGeneration"

print("DesignGeneration")
get_difficulty_res()