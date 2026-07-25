import matplotlib
# matplotlib.use('TKAgg')
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter

# 读取JSON文件
with open('./annotation_results/result_generation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 定义模型顺序和显示名称
models_order = [
    "Llama-3.2-11B-Vision-Instruct",
    "Llama-3.2-90B-Vision-Instruct",
    "qwen2.5-vl-7b-instruct",
    "qwen2.5-vl-72b-instruct",
    "pixtral-12b-2409",
    "pixtral-large-latest",
    "gemini-2.0-flash",
    "gpt-4o-2024-11-20",
    "claude-3-7-sonnet-20250219",
    "gemini-2.5-pro",
    "gpt-5",
    "claude-sonnet-4-20250514",
    "gemini-3.1-pro-preview",
    "gpt-5.4-2026-03-05",
    "claude-sonnet-4-6"
]

models_display_names = [
    "Llama-11B",
    "Llama-90B",
    "Qwen-7B",
    "Qwen-72B",
    "Pixtral-12B",
    "Pixtral-124B",
    "Gemini-2.0",
    "GPT-4o",
    "Claude-3.7",
    "Gemini-2.5",
    "GPT-5",
    "Claude-4",
    "Gemini-3.1",
    "GPT-5.4",
    "Claude-4.6"
]


labels = ["compile error",
          "layout disorder",
          "element position",
          "element color",
          "element text",
          "element size",
          "element missing",
          "good generation"]


# 为每个类别定义颜色
colors = [
    '#FF6B6B',  # compile error - 红色
    '#FFA07A',  # no repair - 浅红色
    '#8dd3c7',  # wrong object - 橙色
    '#FFCCCB',  # wrong repair - 粉红色
    '#87CEEB',  # partial repair - 天蓝色
    '#bebada',  # unnecessary modifications - 浅绿色
    '#ffe699',
    '#90EE90'  # good repair - 绿色
]

# 统计每个模型的类别分布，按指定顺序
model_stats_ordered = []
display_names_filtered = []


for model_name, display_name in zip(models_order, models_display_names):
    if model_name in data:
        frameworks = data[model_name]
        # 收集该模型所有结果
        all_results = []
        for framework, results in frameworks.items():
            # if isinstance(results, list):
            #     for res in results:
            #         all_results.extend(res)
            # else:
            # print(results.values())
            for item in results.values():
                item = [x for x in item if x != ""]
                all_results.extend(item)
            # all_results.extend(results.values())

        # 统计各类别数量
        category_counts = Counter(all_results)
        total_count = len(all_results)

        # 计算百分比，按照指定顺序
        percentages = []
        for label in labels:
            count = category_counts.get(label, 0)
            percentage = (count / total_count) * 100
            percentages.append(percentage)

        model_stats_ordered.append(percentages)
        display_names_filtered.append(display_name)

# 转换为numpy数组
data_matrix = np.array(model_stats_ordered)

# 创建横向堆叠柱状图
# fig, ax = plt.subplots(figsize=(11, 8))
fig, ax = plt.subplots(figsize=(12.5, 8))

# 创建横向堆叠柱状图
left = np.zeros(len(display_names_filtered))
bar_height = 0.6


labels = ["compile error",
          "layout disorder",
          "wrong position",
          "wrong color",
          "wrong text",
          "wrong size",
          "element missing",
          "good generation"]

for i, (label, color) in enumerate(zip(labels, colors)):
    values = data_matrix[:, i]
    print(values)
    bars = ax.barh(display_names_filtered, values, left=left, height=bar_height,
                   label=label, color=color, alpha=0.8)
    left += values

    # 在柱子上添加百分比标签（只显示大于3%的）
    for j, (bar, value) in enumerate(zip(bars, values)):
        if value > 3:  # 只显示大于3%的标签
        # if value > 4:  # 只显示大于3%的标签
            ax.text(left[j] - value / 2, bar.get_y() + bar.get_height() / 2,
                    f'{value:.1f}%', ha='center', va='center',
                    fontsize=12, fontweight='bold')

# 设置图表属性
ax.set_xlabel('Percentage (%)', fontsize=24)
ax.set_ylabel('Model', fontsize=24)

# 设置x轴范围为0-100%
ax.set_xlim(0, 100)
ax.tick_params(axis='x', labelsize=24)
ax.tick_params(axis='y', labelsize=24)

# 添加网格
ax.grid(True, axis='x', alpha=0.3)

# 设置图例
ax.legend(bbox_to_anchor=(0.35, 1.15), loc='upper center', fontsize=20, ncol=4, frameon=False,
labelspacing=0.1, handletextpad=0.1, columnspacing=0.2
          )

# 调整布局
plt.tight_layout()

plt.savefig("./figure/generation_failure.pdf")

# 显示图表
plt.show()

# # 打印详细统计信息
# print("\n各模型详细统计信息:")
# print("=" * 80)
# for model_name, display_name, percentages in zip(models_order, models_display_names, model_stats_ordered):
#     if model_name in data:
#         print(f"\n{display_name} ({model_name}):")
#         total_items = sum(Counter(result for framework in data[model_name].values()
#                                   for result in framework.values()).values())
#         print(f"  总样本数: {total_items}")
#
#         for label, percentage in zip(labels, percentages):
#             count = int(percentage * total_items / 100)
#             print(f"  {label:25}: {count:3d} ({percentage:5.1f}%)")