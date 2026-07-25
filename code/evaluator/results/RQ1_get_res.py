import json
import re
from collections import defaultdict
from pathlib import Path


# 框架名映射：文件名中的关键词 -> 输出中的框架名
FRAMEWORK_MAP = {
    "react": "React",
    "vue": "Vue",
    "angular": "Angular",
    "vanilla": "Vanilla",
}

FRAMEWORK_ORDER = ["React", "Vue", "Angular", "Vanilla"]

METRIC_LABELS = {
    "clip_similarity": "CLIP",
    "structure_similarity": "SSIM",
    "compile_success_rate": "CSR",
    "llm_score": "MLLM Score",
    "ast_code_op_score": "CMLS",
    "ast_code_content_weighted_score": "CMCS",
}

METRIC_ORDER = [
    "clip_similarity",
    "structure_similarity",
    "compile_success_rate",
    "llm_score",
    "ast_code_op_score",
    "ast_code_content_weighted_score",
    "code_score",
    "issue accuracy",
    "MAE",
    "ast_code_content_score",
]

VISUAL_METRICS = {"MAE", "clip_similarity", "structure_similarity"}

MODEL_DISPLAY_ORDER = [
    ("claude-sonnet-4-6", "Claude-4.6"),
    ("gpt-5.4-2026-03-05", "GPT-5.4"),
    ("gemini-3.1-pro-preview", "Gemini-3.1"),
    ("claude-sonnet-4-20250514", "Claude-4"),
    ("gpt-5", "GPT-5"),
    ("gemini-2.5-pro", "Gemini-2.5"),
    ("claude-3-7-sonnet-20250219", "Claude-3.7"),
    ("gpt-4o-2024-11-20", "GPT-4o"),
    ("gemini-2.0-flash", "Gemini-2.0"),
    ("Llama-3.2-90B-Vision-Instruct", "Llama-90B"),
    ("Llama-3.2-11B-Vision-Instruct", "Llama-11B"),
    ("pixtral-large-latest", "Pixtral-124B"),
    ("pixtral-12b-2409", "Pixtral-12B"),
    ("qwen2.5-vl-72b-instruct", "Qwen-72B"),
    ("qwen2.5-vl-7b-instruct", "Qwen-7B"),
]

MODEL_DISPLAY_NAMES = dict(MODEL_DISPLAY_ORDER)
MODEL_ORDER_INDEX = {model: index for index, (model, _name) in enumerate(MODEL_DISPLAY_ORDER)}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_framework(filename: str):
    """从文件名中识别框架名，未匹配返回 None。"""
    lower = filename.lower()
    for key, name in FRAMEWORK_MAP.items():
        if key in lower:
            return name
    return None


def is_compile_success(metrics: dict) -> bool:
    """
    判断单个 sample 是否编译成功。
    约定：compile_error 缺失、None、空字符串或 "NULL" 都视为成功。
    其他非空内容视为失败。
    """
    value = metrics.get("compile_error")
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().upper() in {"", "NULL"}
    return False


def parse_llm_score(value):
    """
    从 llm score 字段中用正则提取 score，不依赖 JSON 解析。
    """
    if not isinstance(value, str):
        return None

    pattern = r'"score"\s*:\s*(\d+(?:\.\d+)?)'
    # match = re.search(pattern, value)
    match = re.search(pattern, value, flags=re.IGNORECASE)
    # if match:
    #     return float(match.group(1))
    if match:
        return int(match.group(1))
    return None


# def parse_llm_score(value):
#     """
#     从 llm score 字段中用正则提取 score，不依赖 JSON 解析。
#     """
#     if not isinstance(value, str):
#         return None
#
#     pattern = r'"score"\s*:\s*(\d+(?:\.\d+)?)'
#     match = re.search(pattern, value, )
#     if match:
#         return float(match.group(1))
#     return None


def aggregate_task(task_dir: Path) -> dict:
    """
    处理单个 task 目录，返回聚合结果：
    { framework: { model: { metric: avg_value, compile_success_rate: rate } } }
    """
    # framework -> model -> metric -> [values]
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # framework -> model -> compile counters
    compile_total = defaultdict(lambda: defaultdict(int))
    compile_success = defaultdict(lambda: defaultdict(int))

    for json_file in sorted(task_dir.glob("*.json")):
        if "_image" in str(json_file) or "_code" in str(json_file):
            continue
        framework = detect_framework(json_file.stem)
        if framework is None:
            print(f"[跳过] 无法识别框架：{json_file.name}")
            continue

        try:
            content = load_json(json_file)
        except json.JSONDecodeError as e:
            print(f"[跳过] 解析失败 {json_file}: {e}")
            continue

        for model_name, model_data in content.items():
            if not isinstance(model_data, dict):
                continue

            for sample_id, metrics in model_data.items():
                if not isinstance(metrics, dict):
                    continue

                compile_total[framework][model_name] += 1
                sample_compile_success = is_compile_success(metrics)
                if sample_compile_success:
                    compile_success[framework][model_name] += 1

                for metric_name, value in metrics.items():
                    # compile_error 是错误信息文本；如果它表示失败，仅视觉指标和 llm_score 按 0 参与平均。
                    if metric_name == "compile_error":
                        continue
                    if metric_name == "llm score":
                        if sample_compile_success:
                            score = parse_llm_score(value)
                            if score is not None:
                                data[framework][model_name]["llm_score"].append(score)
                        else:
                            data[framework][model_name]["llm_score"].append(0.0)
                        continue
                    if isinstance(value, (int, float)):
                        data[framework][model_name][metric_name].append(
                            0.0 if (not sample_compile_success and metric_name in VISUAL_METRICS) else float(value)
                        )
                        # data[framework][model_name][metric_name].append(
                        #     float(value) if (not sample_compile_success and metric_name in VISUAL_METRICS) else float(value)
                        # )

    # 计算均值，保留4位小数
    result = {}
    frameworks = sorted(set(data.keys()) | set(compile_total.keys()))
    for framework in frameworks:
        result[framework] = {}
        models = sorted(set(data[framework].keys()) | set(compile_total[framework].keys()))

        for model_name in models:
            if "claude-sonnet-4-6" in model_name:
                print("")
            result[framework][model_name] = {
                metric: round(sum(vals) / len(vals), 4)
                for metric, vals in data[framework][model_name].items()
                if vals
            }

            total = compile_total[framework][model_name]
            if total:
                result[framework][model_name]["compile_success_rate"] = round(
                    compile_success[framework][model_name] / total,
                    4,
                )

    return result


def save_json(data: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[完成] 已保存：{path}")


def format_table_value(value) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.4f}"
    return "-"


def collect_models(data: dict) -> list[str]:
    models = set()
    for framework_data in data.values():
        if isinstance(framework_data, dict):
            models.update(framework_data.keys())
    return sorted(models, key=lambda model: (MODEL_ORDER_INDEX.get(model, len(MODEL_ORDER_INDEX)), model))


def display_model_name(model_name: str) -> str:
    return MODEL_DISPLAY_NAMES.get(model_name, model_name)


def collect_metrics(data: dict) -> list[str]:
    metrics = set()
    for framework_data in data.values():
        if not isinstance(framework_data, dict):
            continue
        for model_data in framework_data.values():
            if isinstance(model_data, dict):
                metrics.update(model_data.keys())

    return sorted(
        metrics,
        key=lambda metric: (
            METRIC_ORDER.index(metric) if metric in METRIC_ORDER else len(METRIC_ORDER),
            metric,
        ),
    )


def render_markdown_table(data: dict, metrics: list[str]) -> str:
    frameworks = [fw for fw in FRAMEWORK_ORDER if fw in data]
    models = collect_models(data)
    headers = ["Model"] + [
        f"{METRIC_LABELS.get(metric, metric)}-{framework}"
        for metric in metrics
        for framework in frameworks
    ]

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for model_name in models:
        row = [model_name]
        for metric in metrics:
            for framework in frameworks:
                value = data.get(framework, {}).get(model_name, {}).get(metric)
                row.append(format_table_value(value))
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def render_console_table(data: dict, metrics: list[str]) -> str:
    frameworks = [fw for fw in FRAMEWORK_ORDER if fw in data]
    models = collect_models(data)
    metric_labels = [METRIC_LABELS.get(metric, metric) for metric in metrics]

    model_width = max([len("Model"), *(len(display_model_name(model)) for model in models)] or [len("Model")])
    col_widths = {}
    for metric, label in zip(metrics, metric_labels):
        for framework in frameworks:
            values = [
                format_table_value(data.get(framework, {}).get(model, {}).get(metric))
                for model in models
            ]
            col_widths[(metric, framework)] = max(len(framework), len(label), *(len(value) for value in values))

    group_segments = []
    framework_segments = []
    for metric, label in zip(metrics, metric_labels):
        widths = [col_widths[(metric, framework)] for framework in frameworks]
        group_width = sum(widths) + len(" | ") * (len(widths) - 1)
        group_segments.append(label.center(group_width))
        framework_segments.append(
            " | ".join(framework.center(col_widths[(metric, framework)]) for framework in frameworks)
        )

    header_1 = "Model".ljust(model_width) + " || " + " || ".join(group_segments)
    header_2 = " " * model_width + " || " + " || ".join(framework_segments)
    separator = "-" * len(header_2)
    lines = [header_1, header_2, separator]

    for model in models:
        cells = []
        for metric in metrics:
            for framework in frameworks:
                value = data.get(framework, {}).get(model, {}).get(metric)
                cells.append(format_table_value(value).rjust(col_widths[(metric, framework)]))

        metric_cells = []
        cursor = 0
        for metric in metrics:
            metric_cells.append(" | ".join(cells[cursor:cursor + len(frameworks)]))
            cursor += len(frameworks)
        lines.append(display_model_name(model).ljust(model_width) + " || " + " || ".join(metric_cells))

    return "\n".join(lines)


def print_task_tables(task_name: str, data: dict) -> None:
    metrics = collect_metrics(data)
    if not metrics:
        print(f"\n[{task_name}] 无可打印指标")
        return

    visual_metrics = [
        metric for metric in ["clip_similarity", "structure_similarity", "compile_success_rate"]
        if metric in metrics
    ]
    code_metrics = [
        metric for metric in ["llm_score", "compile_success_rate", "ast_code_op_score", "ast_code_content_weighted_score"]
        if metric in metrics
    ]
    other_metrics = [
        metric for metric in metrics
        if metric not in set(visual_metrics) | set(code_metrics)
    ]

    print(f"\n===== {task_name} / Visual Metrics =====")
    print(render_console_table(data, visual_metrics))

    if code_metrics and code_metrics != visual_metrics:
        print(f"\n===== {task_name} / Code & Judge Metrics =====")
        print(render_console_table(data, code_metrics))

    if other_metrics:
        print(f"\n===== {task_name} / Other Metrics =====")
        print(render_console_table(data, other_metrics))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="聚合 res 文件夹下各模型各指标的平均值")
    parser.add_argument("--res_dir", default="res", help="结果文件夹路径（默认：res）")
    parser.add_argument("--output_dir", default=".", help="输出目录（默认：当前目录）")
    args = parser.parse_args()

    res_path = Path(args.res_dir)
    if not res_path.exists():
        print(f"[错误] 目录不存在：{args.res_dir}")
        return

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    task_dirs = [d for d in sorted(res_path.iterdir()) if d.is_dir()]
    if not task_dirs:
        print(f"[警告] {res_path} 下未找到任何子目录")
        return

    for task_dir in task_dirs:
        task_name = task_dir.name
        print(f"\n正在处理：{task_name}")
        result = aggregate_task(task_dir)

        if not result:
            print(f"  [警告] {task_name} 下未聚合到任何数据")
            continue

        out_file = output_path / f"{task_name}.json"
        save_json(result, out_file)
        print_task_tables(task_name, result)


if __name__ == "__main__":
    main()
