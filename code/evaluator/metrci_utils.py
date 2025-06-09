import subprocess
import re
from selenium.webdriver.firefox.service import Service
import base64
from selenium import webdriver
import time
import os
from selenium.webdriver.firefox.options import Options
import json
from selenium.webdriver.support.wait import WebDriverWait
from config import *


class WebDriver:
    def __init__(self, browser_name='firefox', url=None, file=None, string=None, headless=None):
        self.browser_name = browser_name
        self.init_url = None
        self.headless = headless
        self.url = url
        self.file = file
        self.string = string
        self.main_window = None
        self.driver = self.create_driver()

    def create_driver(self):
        service = Service()
        options = Options()
        if self.headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options, service=service)

        if self.file:
            driver.get("file:///" + os.getcwd() + "/" + self.file)
            self.init_url = "file:///" + os.getcwd() + "/" + self.file
        elif self.string:
            string = base64.b64encode(self.string.encode('utf-8')).decode()
            driver.get("data:text/html;base64," + string)
        elif self.url:
            driver.get(self.url)
            self.init_url = self.url

        driver.maximize_window()
        self.main_window = driver.current_window_handle
        return driver

    def take_screenshot(self, filename):
        if self.browser_name == "chrome":
            self.driver.save_screenshot(filename)
        else:
            self.driver.save_full_page_screenshot(filename)

    def quit(self):
        self.driver.quit()


def validate_issue(res_path, config_path):
    with open(config_path, "r") as fs:
        ground_truth = json.loads(fs.read())
        issues = ground_truth["issue"]
    with open(res_path, "r") as fs:
        generated = json.loads(fs.read())
        # generated_issue = generated["Display issues"]
        generated_issue = generated["Issues"]

    if not (type(issues) is list):
        issues = set([issues])
    else:
        issues = set(issues)
    if not (type(generated_issue) is list):
        generated_issue = set([generated_issue])
    else:
        generated_issue = set(generated_issue)

    generated_issue = set(generated_issue)
    print(generated_issue)

    if len(generated_issue) >= 5 or len(generated_issue) == 0:
        return 0
    else:
        return len(issues.intersection(generated_issue)) / len(issues.union(generated_issue))


# def remove_comments(file_path):
def remove_comments(content):
    """
    从Vue或React文件中删除注释

    Args:
        file_path: 要处理的文件路径

    Returns:
        str: 处理后的无注释文件内容
    """
    # 读取文件内容
    # try:
    #     with open(file_path, 'r', encoding='utf-8') as file:
    #         content = file.read()
    # except Exception as e:
    #     print(f"无法读取文件 {file_path}: {e}")
    #     return None

    # 用于存储结果
    result = content

    # 1. 移除多行JavaScript注释 (/* ... */)
    result = re.sub(r'/\*[\s\S]*?\*/', '', result)

    # 2. 移除单行JavaScript注释 (// ...)
    # result = re.sub(r'//.*?$', '', result, flags=re.MULTILINE)

    # 3. 如果是Vue文件，移除HTML注释 (<!-- ... -->)
    # if file_path.endswith('.vue'):
    result = re.sub(r'<!--[\s\S]*?-->', '', result)

    # 4. 移除空行（包括只有空白字符的行）
    # 首先按行分割
    lines = result.split('\n')
    # 过滤掉空行或只包含空白字符的行
    non_empty_lines = [line for line in lines if line.strip()]
    # 重新组合成文本
    result = '\n'.join(non_empty_lines)

    # 4. 处理特殊情况：保留有用的正则表达式中的注释符号
    # 例如 let regex = /\/\//; 不应被错误处理
    # 这需要更复杂的解析，但这里使用简单方法

    return result


def save_html(link, filename):
    os.system(f"npx single-file {link} {filename}")


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
