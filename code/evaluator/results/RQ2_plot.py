import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42


def get_res(file_name):
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
    key = "Compile"
    # key = "CLIP"
    print(df[key])

    # res = " & ".join(map(str, list(df[key])))
    res = " & ".join([f"{x:.4f}" for x in list(df[key])])

    # res = " & ".join([f"{x:.2%}" for x in df[key]])

    print("& " + res + " \\" + "\\")

    # print(df[key].mean())

    # return np.array(df[key])
    return df[key].mean()


#
# frame_works = ["react", "vue", "angular", "vanilla"]
# implemented =  ["react", "vue", "angular", "vanilla"]
#
#
# res = np.zeros((4, 4))
#
# for (i, frame) in enumerate(frame_works):
#     for (j, implement) in enumerate(implemented):
#         res[i][j] = get_res(f"./designgeneration/res_{frame}_{implement}.json")
#
# print(res)
#

# 数据
data = np.array([
    [0.65555556, 0.61451111, 0.556, 0.7791],
    [0.63988889, 0.60054444, 0.55205556, 0.75617778],
    [0.66992222, 0.63654444, 0.50456667, 0.77457778],
    [0.62146667, 0.5503, 0.46347778, 0.7285]
])

# data = np.array([[0.84302222, 0.77066667, 0.70437778, 1.        ],
#  [0.82863333, 0.7599, 0.70714444, 1.        ],
#  [0.84874444, 0.77911111, 0.62782222, 1.        ],
#  [0.86483333, 0.74813333, 0.63705556, 1.        ]])

# data = res

x_labels = ["React", "Vue", "Angular", "Vanilla"]
y_labels =  ["React", "Vue", "Angular", "Vanilla"]

# 设置图形大小和样式
plt.figure(figsize=(10, 8))

# 创建热力图，使用与参考图相似的颜色映射
ax = sns.heatmap(data,
                 xticklabels=x_labels,
                 yticklabels=y_labels,
                 annot=True,  # 显示数值
                 fmt='.4',   # 百分比格式，保留1位小数
                 cmap='YlGnBu',  # 黄-绿-蓝色彩映射，类似参考图
                 square=True,  # 正方形单元格
                 # linewidths=1,  # 网格线宽度
                 # linecolor='white',  # 白色网格线
                 cbar_kws={'shrink': 0.95},
                 # cbar=False,
                 # annot_kws={'fontsize': 21, 'fontweight': 'bold'}
                 annot_kws={'fontsize': 25}
                 )


cbar = ax.collections[0].colorbar
cbar.set_ticks([])  # 移除所有刻度
cbar.set_label('')  # 移除标签

# 设置标题
# plt.title('CLIP Score', fontsize=20, fontweight='bold', pad=20)

# 设置轴标签
# plt.xlabel('Implemented Framework', fontsize=20, fontweight='bold')
# plt.ylabel('Webpage Framework', fontsize=20, fontweight='bold')

plt.xlabel('Implemented Framework', fontsize=28)
plt.ylabel('Webpage Framework', fontsize=28)


# 调整标签样式
plt.xticks(fontsize=28)
plt.yticks(fontsize=28, rotation=0)

# 调整布局
plt.tight_layout()
# plt.savefig("./figure/compile.pdf")
plt.savefig("./figure/clip.pdf")
plt.show()