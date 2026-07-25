import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import rcParams

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42


def plot_error_distribution(frame="vue"):
    # frame = "angular"
    if frame == "vue":
        data = {
            "claude-sonnet-4-6": {
                "Duplicate Attribute": 3,
                "Unexpected Token": 2
            },
            "gpt-5.4-2026-03-05": {
                "Attribute Error": 1,
                "Missing End Tag": 1
            },
            "gemini-3.1-pro-preview": {
                "Missing End Tag": 5,
                "Illegal Slash": 1,
                "Unexpected EOF": 6
            },
            "claude-sonnet-4-20250514": {
                "Unexpected EOF": 1,
                "Unterminated String Constant": 1,
                "Unknown Utility Class": 1
            },
            "gpt-5": {
                "Missing End Tag": 1,
                "Template Error": 2
            },
            "gemini-2.5-pro": {
                "Unexpected EOF": 1,
                "Could not resolve value": 1,
                "Missing End Tag": 1
            },
            "claude-3-7-sonnet-20250219": {
                "Unknown Utility Class": 1
            },
            "gpt-4o-2024-11-20": {
                "Missing End Tag": 2,
                "Unexpected Token": 1
            },
            "gemini-2.0-flash": {
                "Unexpected EOF": 15,
                "Import Error": 2,
                "Missing End Tag": 2
            },
            "Llama-3.2-90B-Vision-Instruct": {
                "Missing End Tag": 2,
                "No Template": 11,
                "Unexpected Token": 7,
                "Import Error": 2
            },
            "Llama-3.2-11B-Vision-Instruct": {
                "Missing End Tag": 20,
                "Unknown Utility Class": 21,
                "Multiple Template in Single File": 1,
                "Import Error": 2,
                "Unexpected Token": 2,
                "Unexpected EOF": 2
            },
            "pixtral-large-latest": {
                "Import Error": 1,
                "Unexpected EOF": 2
            },
            "pixtral-12b-2409": {
                "Missing End Tag": 1,
                "Tailwind Export Error": 1,
                "Unknown Utility Class": 2,
                "Import Error": 2,
                "Unexpected EOF": 1
            },
            "qwen2.5-vl-72b-instruct": {
                "Unexpected EOF": 4,
                "Import Error": 4,
                "Unexpected Token": 2,
                "Unknown Utility Class": 1
            },
            "qwen2.5-vl-7b-instruct": {
                "Duplicate attribute.": 8,
                "Illegal Slash": 10,
                "Missing End Tag": 17,
                "Unexpected EOF": 8,
                "Missing Closing Brace": 3,
                "Attribute Name Error": 29,
                "Invalid End Tag": 16,
                "Unquoted Attribute Error": 2,
                "Unexpected Token": 6,
                "Transition Error": 1,
                "Duplicate Identifier": 1,
                "Side Effect Tags": 1
            }
        }
    elif frame == "react":
        data = {
            "claude-sonnet-4-6": {},
            "gemini-3.1-pro-preview": {
                "Unexpected Token": 6,
                "Use Client Missing": 1,
                "Unterminated String Constant": 1
            },
            "gpt-5.4-2026-03-05": {},
            "claude-sonnet-4-20250514": {
                "Unexpected Token": 1
            },
            "gpt-5": {
                "Unterminated String Constant": 2,
                "Use Client Missing": 1
            },
            "gemini-2.5-pro": {
                "Unexpected Token": 4,
                "Use Client Missing": 4,
                "Cannot reassign to an imported binding": 1
            },
            "claude-3-7-sonnet-20250219": {
                "Use Client Missing": 2,
                "Unexpected Token": 3
            },
            "gpt-4o-2024-11-20": {
                "Unterminated String Constant": 2,
                "Use Client Missing": 1
            },
            "gemini-2.0-flash": {
                "Unexpected Token": 10
            },
            "Llama-3.2-90B-Vision-Instruct": {
                "Unexpected Token": 4,
                "Unterminated String Constant": 1,
                "Unexpected EOF": 1
            },
            "Llama-3.2-11B-Vision-Instruct": {
                "Unexpected Token": 9,
                "Use Client Missing": 2
            },
            "pixtral-large-latest": {
                "Use Client Missing": 2,
                "Unexpected Token": 1
            },
            "pixtral-12b-2409": {
                "Variable Defined Multiple Times": 6,
                "Unexpected Token": 6,
                "Use Client Missing": 3,
                "Unexpected EOF": 1
            },
            "qwen2.5-vl-72b-instruct": {
                "Unexpected Token": 5
            },
            "qwen2.5-vl-7b-instruct": {
                "Unexpected Token": 44,
                "Expression Expected": 47,
                "Function not Supported in app/": 1,
                "Identifier Cannot Follow Number": 1,
                "Unterminated String Constant": 1,
                "Import or Export Error": 1
            }
        }
    else:
        data = {
            "claude-sonnet-4-6": {
                "Not assignable": 3,
                "Incomplete Block": 17,
                "Property Error": 1,
                "Property does not exist on type": 1
            },
            "gemini-3.1-pro-preview": {
                "Incomplete Block": 15,
                "Invalid ICU Message": 2,
                "Not assignable": 2,
                "Property is missing in type": 1
            },
            "gpt-5.4-2026-03-05": {
                "Not assignable": 1,
                "Incomplete Block": 18,
                "Invalid ICU Message": 1,
                "Binding Errors": 1,
                "Property is missing in type": 1,
                "Property does not exist on type": 1,
                "Unexpected Token": 1
            },
            "claude-sonnet-4-20250514": {
                "Unable to initialize JavaScript cache storage": 27
            },
            "gemini-2.5-pro": {
                "Unable to initialize JavaScript cache storage": 26
            },
            "gpt-5": {
                "Unable to initialize JavaScript cache storage": 27
            },
            "claude-3-7-sonnet-20250219": {
                "Incomplete Block": 23,
                "Unexpected Token": 1,
                "Property Error": 1,
                "Invalid ICU Message": 1
            },
            "gpt-4o-2024-11-20": {
                "Incomplete Block": 22,
                "Invalid ICU Message": 2
            },
            "gemini-2.0-flash": {
                "Incomplete Block": 20,
                "Invalid ICU Message": 2,
                "Component Define Error": 2
            },
            "Llama-3.2-90B-Vision-Instruct": {
                "Incomplete Block": 11,
                "Component Import Error": 7,
                "Binding Errors": 2,
                "Property Error": 1,
                "Component Define Error": 1
            },
            "Llama-3.2-11B-Vision-Instruct": {
                "Component Export Error": 3,
                "Component Import Error": 19,
                "Incomplete Block": 1,
                "Unexpected Token": 2
            },
            "pixtral-large-latest": {
                "Incomplete Block": 17,
                "Invalid ICU Message": 2,
                "Property Error": 1
            },
            "pixtral-12b-2409": {
                "Property Error": 4,
                "Incomplete Block": 13,
                "Component Export Error": 13,
                "Invalid ICU Message": 3
            },
            "qwen2.5-vl-72b-instruct": {
                "Component Import Error": 4,
                "Incomplete Block": 21,
                "Invalid ICU Message": 2,
                "Binding Errors": 2,
                "Component Define Error": 1,
                "Property Error": 1
            },
            "qwen2.5-vl-7b-instruct": {
                "Unexpected Token": 8,
                "Tag Error": 27,
                "Incomplete Block": 8,
                "Component Export Error": 1,
                "Component Define Error": 8,
                "Property Error": 3,
                "Unexpected Closing Tag": 11,
                "Component Import Error": 1,
                "Missing Reference Target": 1,
                "Unable to Parse Entity": 1,
                "Invalid ICU Message": 3,
                "Unexpected Closing Block": 1
            }
        }

    # 简化模型名称
    model_name_mapping = {
        'claude-sonnet-4-6': "Claude-4.6",
        "gpt-5.4-2026-03-05": "GPT-5.4",
        'gemini-3.1-pro-preview': "Gemini-3.1",
        "claude-sonnet-4-20250514": "Claude-4",
        "gpt-5": "GPT-5",
        "gemini-2.5-pro": "Gemini-2.5",
        'claude-3-7-sonnet-20250219': 'Claude-3.7',
        'gpt-4o-2024-11-20': 'GPT-4o',
        'gemini-2.0-flash': 'Gemini-2.0',
        'Llama-3.2-90B-Vision-Instruct': 'Llama-90B',
        'Llama-3.2-11B-Vision-Instruct': 'Llama-11B',
        'pixtral-large-latest': 'Pixtral-124B',
        'pixtral-12b-2409': 'Pixtral-12B',
        'qwen2.5-vl-72b-instruct': 'Qwen-72B',
        'qwen2.5-vl-7b-instruct': 'Qwen-7B'
    }

    # === 修改：原来的代码在 if/elif/else 之外直接使用只在 else 分支里定义的 error_dic，
    #     当 frame == "react" 或 "vue" 时 error_dic 根本不存在，会直接 NameError。
    #     现在改为：无论 frame 是哪个分支，都直接从当前使用的 data 里动态统计每种错误类型的总次数。
    #     同时显式跳过空 dict 的模型（例如 "claude-sonnet-4-6": {}，表示该模型没有任何报错），
    #     避免在统计/排序时出问题。 ===
    error_dic = {}
    for errors in data.values():
        if not errors:  # 修改：处理某个模型错误 dict 为空的情况，直接跳过，不参与错误类型统计
            continue
        for error_type, count in errors.items():
            error_dic[error_type] = error_dic.get(error_type, 0) + count

    all_error_types = sorted(error_dic.keys(), key=lambda x: error_dic[x], reverse=True)
    # === 修改结束 ===

    print(all_error_types)

    # 转换为DataFrame格式
    df_data = []
    for model, errors in data.items():
        model_simple = model_name_mapping.get(model, model)
        # 修改：errors 为空 dict 时 sum({}.values()) 本来就是 0，这里保持不变，
        # 只是补充注释说明这是被支持的场景（total 会是 0）
        total_errors = sum(errors.values())
        row = {'model': model_simple, 'total': total_errors}

        for error_type in all_error_types:
            row[error_type] = errors.get(error_type, 0)

        df_data.append(row)

    df = pd.DataFrame(df_data)

    # 按总错误数排序
    df = df.sort_values('total', ascending=True)  # ascending=True 使得最大值在上方

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # pd.set_option('max_colwidth', 1000)
    # pd.set_option('display.width', 5000)

    # 准备绘图数据
    models = df['model'].values
    error_columns = [col for col in df.columns if col not in ['model', 'total']]

    # === 修改：如果所有模型的错误 dict 都是空的（极端情况），error_columns 会是空列表，
    #     直接给出明确报错，而不是让 plt.cm.tab20 / 后续绘图逻辑产生难以理解的异常 ===
    if len(error_columns) == 0:
        raise ValueError("data 中所有模型的错误 dict 都为空，没有可绘制的错误类型，请检查数据。")
    # === 修改结束 ===

    # 创建颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, len(error_columns)))

    # 创建图形
    if frame == "angular":
        fig, ax = plt.subplots(figsize=(14, 7))
    else:
        fig, ax = plt.subplots(figsize=(14, 6))

    # 为每个模型按错误数量排序错误类型
    def sort_errors_for_model(row):
        """为每个模型的错误类型按数量排序。
        修改：当该模型的错误 dict 为空时，row 里对应的所有 error_type 列都是 0，
        这里会自然返回空列表 []，对应的模型在图上只会显示总数 0，不会画出任何堆叠色块，
        这是符合预期的行为，无需额外处理。"""
        error_dict = {}
        for col in error_columns:
            if row[col] > 0:
                error_dict[col] = row[col]
        return sorted(error_dict.items(), key=lambda x: x[1], reverse=True)

    # === 修改：原来直接用 models[i]（字符串）作为 barh 的 y 坐标，
    #     matplotlib 的字符串类别轴只有"被 barh 画过"的类别才会出现在 y 轴上。
    #     如果某个模型 sorted_errors 是空的（错误 dict 为空），它就从来没被 barh 调用过，
    #     这个模型的 y 轴刻度可能根本不出现，而不只是"看起来是空的"。
    #     改用数值型 y 坐标（y_pos），并在循环结束后显式 set_yticks/set_yticklabels，
    #     这样无论有没有画过 bar，每个模型都一定会在 y 轴上占一行。 ===
    y_pos = np.arange(len(models))
    # === 修改结束 ===

    # 绘制堆叠横向柱状图
    bars = []
    legend_added = set()  # 跟踪已添加到图例的错误类型
    zero_length_shown = False  # 修改：用于图例只标注一次"无错误"标记

    for i, (_, row) in enumerate(df.iterrows()):
        left_pos = 0
        sorted_errors = sort_errors_for_model(row)

        if not sorted_errors:
            # === 修改：total 为 0 的模型（错误 dict 为空），显式画一个很短但可见的
            #     灰色标记条，代表"长度为0的坐标轴/柱子"，而不是完全不画，
            #     避免这一行在图上彻底消失或让人误以为数据缺失。 ===
            bar = ax.barh(y_pos[i], 0.15, left=0,
                          color='lightgray', edgecolor='gray', alpha=0.9, height=0.6,
                          label='No Errors' if not zero_length_shown else "")
            zero_length_shown = True
            bars.append(bar)
            continue
            # === 修改结束 ===

        for error_type, count in sorted_errors:
            error_idx = error_columns.index(error_type)
            # 只有第一次遇到某个错误类型时才添加label
            label = error_type if error_type not in legend_added else ""
            bar = ax.barh(y_pos[i], count, left=left_pos, label=label,
                          color=colors[error_idx], alpha=0.8, height=0.6)

            if error_type not in legend_added:
                legend_added.add(error_type)
                bars.append(bar)

            left_pos += count

    # === 修改：显式设置 y 轴刻度和标签，确保所有模型（包括 total=0 的模型）都出现在坐标轴上 ===
    ax.set_yticks(y_pos)
    ax.set_yticklabels(models)
    # === 修改结束 ===

    # 设置标题和标签
    ax.set_xlabel('Error Counts', fontsize=25)
    ax.set_ylabel('Models', fontsize=25)

    ax.tick_params(axis='x', labelsize=25)  # x轴刻度标签大小
    ax.tick_params(axis='y', labelsize=25)  # y轴刻度标签大小

    # 设置网格
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # 设置图例
    if frame == "vue":
        ax.legend(loc='lower right', fontsize=16, ncol=2, frameon=False)
    else:
        ax.legend(loc='lower right', fontsize=16, ncol=1, frameon=False)

    # 在每个柱子上显示总数（修改：total 为 0 时也会正常显示 "0"，无需特殊处理）
    for i, (model, total) in enumerate(zip(models, df['total'])):
        ax.text(total + 0.5, i, str(total), va='center', fontsize=15, fontweight='bold')

    # 调整布局
    plt.tight_layout()

    import os
    os.makedirs("./figure", exist_ok=True)  # 修改：防止 figure 目录不存在导致 savefig 报错
    plt.savefig(f"./figure/error_{frame}.pdf")
    # 显示图表
    plt.show()


if __name__ == "__main__":
    plot_error_distribution(frame="react")
    plot_error_distribution(frame="vue")
    plot_error_distribution(frame="angular")
