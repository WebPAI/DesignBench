from tqdm import tqdm
from metric import *
from metric_ast import ast_code_similarity


# single_path = "./single_file/single-file-cli-master/single-file"
#
# def save_html(link, filename):
#     # filename = f"{new_folder_path}/{image_index}.html"
#     os.system(f"{single_path} {link} {filename}")


def get_begin_end(framework: Framework, task: Task) -> range:
    # (framework, task): (begin, end)
    task_ranges = {
        (Framework.VANILLA, Task.GENERATION): (1, 120),
        (Framework.REACT, Task.GENERATION): (1, 109),
        (Framework.VUE, Task.GENERATION): (1, 118),
        (Framework.ANGULAR, Task.GENERATION): (1, 83),

        (Framework.VANILLA, Task.EDIT): (1, 80),
        (Framework.REACT, Task.EDIT): (1, 108),
        (Framework.VUE, Task.EDIT): (1, 105),
        (Framework.ANGULAR, Task.EDIT): (1, 66),

        (Framework.VANILLA, Task.REPAIR): (1, 28),
        (Framework.REACT, Task.REPAIR): (1, 28),
        (Framework.VUE, Task.REPAIR): (1, 27),
        (Framework.ANGULAR, Task.REPAIR): (1, 28),

        (Framework.VANILLA, Task.COMPILE): (1, 10),
        (Framework.REACT, Task.COMPILE): (1, 10),
        (Framework.VUE, Task.COMPILE): (1, 10),
        (Framework.ANGULAR, Task.COMPILE): (1, 10),
    }

    try:
        begin, end = task_ranges[(framework, task)]
    except KeyError:
        raise ValueError(f"Invalid combination: {framework.value} {task.value}")

    return range(begin, end + 1)


def get_generation_metric(web_name, model_name, frame_work, implement_framework):
    prediction_path = folder_dic[Task.GENERATION]
    reference_img_path = prediction_path + f"{frame_work}/" + f"{web_name}/{web_name}.png"

    format = format_dic[implement_framework]
    generated_code_path = prediction_path + "GenerationResults/" + f"{frame_work}-{implement_framework}/{model_name}/{frame_work}_{web_name}_{model_name}_{implement_framework}.{format}"
    generated_img_path = generated_code_path.replace(f".{format}", ".png")
    generated_html_path = generated_code_path.replace(f".{format}", ".html")

    if re_calculate:
        if os.path.exists(generated_img_path):
            os.remove(generated_img_path)
        if os.path.exists(generated_html_path):
            os.remove(generated_html_path)

    if not os.path.exists(generated_img_path) or not os.path.exists(generated_html_path):
        compile_flag = render_ui(code_path=generated_code_path, save_path=generated_img_path,
                                 frame_work=implement_framework)
        if not compile_flag:
            metrics = {
                "MAE": 0,
                "clip_similarity": 0,
                "structure_similarity": 0
            }
            return metrics

    reference_img = Image.open(reference_img_path)
    generated_img = Image.open(generated_img_path)

    mae = mae_score(img1=reference_img, img2=generated_img)
    cp_similarity = clip_similarity(reference_img_path, generated_img_path)
    ssim_score = ssim_similarity(reference_img_path, generated_img_path)

    metrics = {
        "MAE": mae,
        "clip_similarity": cp_similarity,
        "structure_similarity": ssim_score
    }

    return metrics


def get_repair_metric(web_name, model_name, framework, mode, llm_judge_flag):
    prediction_path = folder_dic[Task.REPAIR]
    generated_code_path = prediction_path + f"RepairResults/{framework}-{framework}/{model_name}/{framework}_{web_name}_{model_name}_{framework}_{mode}.{format_dic[framework]}"
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
                "structure_similarity": 0,
                "issue accuracy": 0,
                "code_score": 0,
                "ast_code_op_score": 0,  # CMLS
                "ast_code_content_score": 0,
                "ast_code_content_weighted_score": 0  # CMCS
            }
            return metrics

    config_file = prediction_path + f"{framework}/{web_name}/{web_name}.json"

    with open(config_file, "r") as fs:
        config = json.loads(fs.read())

        original_img_path = prediction_path + f"{framework}/{web_name}/{web_name}.png"
        reference_img_path = prediction_path + f"{framework}/{web_name}/repaired.png"
        reference_code_path = prediction_path + f"{framework}/{web_name}/repaired.{format_dic[framework]}"

        # src_code = remove_comments(config["src_code"])
        # reference_code = remove_comments(config["dst_code"])

        if framework == "react":
            src_code = config["component_jsx"]
        else:
            src_code = config["code"]

        with open(reference_code_path, "r") as f_code:
            reference_code = f_code.read()

        with open(generated_code_path, "r") as f_code:
            # generated_code = remove_comments(f_code.read())
            generated_code = f_code.read()

        if llm_judge_flag:
            with open(config_file, "r") as f_config:
                ground_truth = json.loads(f_config.read())
                issues = ground_truth["issue"]
            # llm_score = llm_repair_judge(original_image=original_img_path, edited_image=generated_img_path, instruction=config["prompt"])
            llm_score = llm_repair_judge(original_image=original_img_path, repaired_image=generated_img_path,
                                         reference_image=reference_img_path, issues=issues)
            print(original_img_path, generated_img_path, reference_img_path, issues)

            metrics = {
                "llm score": llm_score
            }
        else:
            if framework == "angular":
                src_angular_code = src_code["html"]
                # reference_angular_code = reference_code["html"]
                reference_angular_code = reference_code
                angular_code_score = code_similarity(src_code=src_angular_code, reference_code=reference_angular_code,
                                                     generated_code=generated_code)
                angular_ast_code_op_score, angular_ast_code_content_score = ast_code_similarity(
                    src_code=src_angular_code, reference_code=reference_angular_code,
                    generated_code=generated_code, framework="vanilla")

                print("angular score:", angular_code_score)
                src_ts_code = src_code["ts"]
                # reference_ts_code = reference_code["ts"]

                with open(reference_code_path.replace(".angular", ".ts"), "r") as f_code:
                    reference_ts_code = f_code.read()

                with open(generated_code_path.replace(".angular", ".ts"), "r") as f_code:
                    # generated_code = remove_comments(f_code.read())
                    generated_code = f_code.read()

                ts_ast_code_op_score, ts_ast_code_content_score = ast_code_similarity(src_code=src_ts_code,
                                                                                      reference_code=reference_ts_code,
                                                                                      generated_code=generated_code,
                                                                                      framework=framework)

                ts_code_score = code_similarity(src_code=src_ts_code, reference_code=reference_ts_code,
                                                generated_code=generated_code)

                print("ts score:", ts_code_score)
                code_score = 0.5 * angular_code_score + 0.5 * ts_code_score
                ast_code_op_score = 0.5 * ts_ast_code_op_score + 0.5 * angular_ast_code_op_score
                ast_code_content_score = 0.5 * ts_ast_code_content_score + 0.5 * angular_ast_code_content_score
            else:
                if framework == "react":
                    src_code = remove_comments(src_code)
                    reference_code = remove_comments(reference_code)
                    generated_code = remove_comments(generated_code)

                code_score = code_similarity(src_code=src_code, reference_code=reference_code,
                                             generated_code=generated_code)

                ast_code_op_score, ast_code_content_score = ast_code_similarity(src_code=src_code,
                                                                                reference_code=reference_code,
                                                                                generated_code=generated_code,
                                                                                framework=framework)

            reference_img = Image.open(reference_img_path)

            generated_img = Image.open(generated_img_path)

            mae = mae_score(img1=reference_img, img2=generated_img)
            cp_score = clip_similarity(reference_img_path, generated_img_path)
            ssim_score = ssim_similarity(reference_img_path, generated_img_path)

            issue_flag = validate_issue(res_path=generated_code_path.replace(f".{format_dic[framework]}", ".json"),
                                        config_path=config_file)

            metrics = {
                "MAE": mae,
                "clip_similarity": cp_score,
                "structure_similarity": ssim_score,
                "code_score": code_score,
                "issue accuracy": issue_flag,
                "ast_code_op_score": ast_code_op_score,  # CMLS
                "ast_code_content_score": ast_code_content_score,
                "ast_code_content_weighted_score": ast_code_op_score * ast_code_content_score  # CMCS
            }

    return metrics


def get_edit_metric(web_name, model_name, framework, mode, llm_judge_flag):
    prediction_path = folder_dic[Task.EDIT]
    generated_code_path = prediction_path + f"EditResults/{framework}-{framework}/{model_name}/{framework}_{web_name}_{model_name}_{framework}_{mode}.{format_dic[framework]}"
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
                "structure_similarity": 0,
                "code_score": 0,
                "ast_code_op_score": 0,  # CMLS
                "ast_code_content_score": 0,
                "ast_code_content_weighted_score": 0  # CMCS
            }
            return metrics

    config_file = prediction_path + f"{framework}/{web_name}/{web_name}.json"

    with open(config_file, "r") as fs:
        config = json.loads(fs.read())

        original_img_path = prediction_path + f"{framework}/{web_name}/{config['src_id']}.png"
        reference_img_path = prediction_path + f"{framework}/{web_name}/{config['dst_id']}.png"

        # src_code = remove_comments(config["src_code"])
        # reference_code = remove_comments(config["dst_code"])
        src_code = config["src_code"]
        reference_code = config["dst_code"]

        with open(generated_code_path, "r") as f_code:
            # generated_code = remove_comments(f_code.read())
            generated_code = f_code.read()

        if llm_judge_flag:
            llm_score = llm_edit_judge(original_image=original_img_path, edited_image=generated_img_path,
                                       instruction=config["prompt"])
            metrics = {
                "llm score": llm_score
            }
        else:
            if framework == "angular":
                src_angular_code = src_code["html"]
                reference_angular_code = reference_code["html"]

                angular_code_score = code_similarity(src_code=src_angular_code, reference_code=reference_angular_code,
                                                     generated_code=generated_code)

                angular_ast_code_op_score, angular_ast_code_content_score = ast_code_similarity(
                    src_code=src_angular_code, reference_code=reference_angular_code,
                    generated_code=generated_code, framework="vanilla")

                print("angular score:", angular_code_score)

                src_ts_code = src_code["ts"]
                reference_ts_code = reference_code["ts"]

                with open(generated_code_path.replace(".angular", ".ts"), "r") as f_code:
                    # generated_code = remove_comments(f_code.read())
                    generated_code = f_code.read()

                ts_code_score = code_similarity(src_code=src_ts_code, reference_code=reference_ts_code,
                                                generated_code=generated_code)

                ts_ast_code_op_score, ts_ast_code_content_score = ast_code_similarity(src_code=src_ts_code,
                                                                                      reference_code=reference_ts_code,
                                                                                      generated_code=generated_code,
                                                                                      framework=framework)

                print("ts score:", ts_code_score)
                code_score = 0.5 * angular_code_score + 0.5 * ts_code_score
                ast_code_op_score = 0.5 * ts_ast_code_op_score + 0.5 * angular_ast_code_op_score
                ast_code_content_score = 0.5 * ts_ast_code_content_score + 0.5 * angular_ast_code_content_score
            else:
                code_score = code_similarity(src_code=src_code, reference_code=reference_code,
                                             generated_code=generated_code)
                ast_code_op_score, ast_code_content_score = ast_code_similarity(src_code=src_code,
                                                                                reference_code=reference_code,
                                                                                generated_code=generated_code,
                                                                                framework=framework)

            reference_img = Image.open(reference_img_path)
            generated_img = Image.open(generated_img_path)
            mae = mae_score(img1=reference_img, img2=generated_img)
            cp_score = clip_similarity(reference_img_path, generated_img_path)
            ssim_score = ssim_similarity(reference_img_path, generated_img_path)

            metrics = {
                "MAE": mae,
                "clip_similarity": cp_score,
                "structure_similarity": ssim_score,
                "code_score": code_score,
                "ast_code_op_score": ast_code_op_score, #CMLS
                "ast_code_content_score": ast_code_content_score,
                "ast_code_content_weighted_score": ast_code_op_score*ast_code_content_score #CMCS
            }

    return metrics



def evaluate_repair(models, frame_works, modes, llm_judge_flag):
    for frame_work in frame_works:

        iterate_range = get_begin_end(framework=frame_work, task=Task.REPAIR)
        for model_name in models:
            for mode in modes:
                res_path = f"./res/DesignRepair/{frame_work}_{mode}.json"
                if os.path.exists(res_path):
                    with open(res_path, "r") as fs:
                        results = json.loads(fs.read())
                else:
                    results = {}

                if model_name not in results:
                    results[model_name] = {}

                # for web_name in tqdm(iterate_range):
                for web_name in tqdm(iterate_range):
                    if not llm_judge_flag:
                        if str(web_name) in results[model_name]:
                            continue
                        metric = get_repair_metric(web_name=str(web_name), model_name=model_name, framework=frame_work,
                                                   mode=mode, llm_judge_flag=False)
                        results[model_name][str(web_name)] = metric
                        print(metric)
                    else:
                        try:
                            if "llm score" in results[model_name][str(web_name)]:
                                continue
                            metric = get_repair_metric(web_name=str(web_name), model_name=model_name, framework=frame_work,
                                                          mode=mode, llm_judge_flag=True)
                            # print(metric)
                            results[model_name][str(web_name)]["llm score"] = metric["llm score"]
                        except Exception as e:
                            print(f"error for {web_name}", e)

                with open(res_path, "w") as fs:
                    fs.write(json.dumps(results, indent=4))


def evaluate_edit(models, frame_works, modes, llm_judge_flag):
    for frame_work in frame_works:
        iterate_range = get_begin_end(framework=frame_work, task=Task.EDIT)
        for model_name in models:
            for mode in modes:
                res_path = f"./res/DesignEdit/{frame_work}_{mode}.json"
                if os.path.exists(res_path):
                    with open(res_path, "r") as fs:
                        results = json.loads(fs.read())
                else:
                    results = {}

                if model_name not in results:
                    results[model_name] = {}

                # for web_name in tqdm(range(1, 10)):
                for web_name in tqdm(iterate_range):

                    if not llm_judge_flag:
                        if str(web_name) in results[model_name]:
                            continue
                        metric = get_edit_metric(web_name=str(web_name), model_name=model_name, framework=frame_work,
                                                 mode=mode, llm_judge_flag=False)
                        results[model_name][str(web_name)] = metric
                        print(metric)
                    else:
                        try:
                            if "llm score" in results[model_name][str(web_name)]:
                                continue
                            metric = get_edit_metric(web_name=str(web_name), model_name=model_name,
                                                     framework=frame_work, mode=mode, llm_judge_flag=True)
                            # print(metric)
                            results[model_name][str(web_name)]["llm score"] = metric["llm score"]
                        except Exception as e:
                            print(f"error for {web_name}", e)

                with open(res_path, "w") as fs:
                    fs.write(json.dumps(results, indent=4))


def evaluate_generation(models, frame_works, implemented_frameworks):
    for frame_work in frame_works:
        iterate_range = get_begin_end(framework=frame_work, task=Task.GENERATION)

        for implement_framework in implemented_frameworks:
            res_path = f"./res/DesignGeneration/{frame_work}_{implement_framework}.json"
            if os.path.exists(res_path):
                with open(res_path, "r") as fs:
                    results = json.loads(fs.read())
            else:
                results = {}

            for model_name in models:
                if model_name not in results:
                    results[model_name] = {}

                for web_name in tqdm(iterate_range):
                    # for web_name in tqdm(range(1, 10)):
                    if str(web_name) in results[model_name]:
                        continue

                    metrics = get_generation_metric(web_name, model_name, frame_work=frame_work,
                                                    implement_framework=implement_framework)
                    print(frame_work, implement_framework, model_name, web_name, metrics)
                    results[model_name][web_name] = metrics

            with open(f"res/DesignGeneration/{frame_work}_{implement_framework}.json", "w") as fs:
                fs.write(json.dumps(results, indent=4))


if __name__ == "__main__":
    re_calculate = False

    models = [
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

    frame_works = ["angular"]
    # implemented_frame_works = ["react"]
    # modes = ["both", "code", "image"]
    # modes = ["both", "code", "image"]
    modes = ["code"]

    evaluate_edit(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=False)
    evaluate_repair(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=False)
    # evaluate_repair(models=models, frame_works=frame_works, modes=modes, llm_judge_flag=True)

    # frame_works = ["react"]
    # implemented_frame_works = ["react"]
    # evaluate_generation(models=models, frame_works=frame_works, implemented_frameworks=implemented_frame_works)



    # print(get_begin_end(framework=Framework.REACT, task=Task.GENERATION))
