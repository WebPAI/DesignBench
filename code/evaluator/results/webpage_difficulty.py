import cv2
import numpy as np
from bs4 import BeautifulSoup
from PIL import Image
import re
from collections import Counter
import math


class WebpageDifficultyAnalyzer:
    def __init__(self, weights=None):
        """
        初始化分析器
        weights: 各项指标的权重字典，默认为均等权重
        """
        self.weights = weights or {
            'ui_size': 0.25,
            'ui_elements': 0.25,
            'color_variety': 0.25,
            'layout_complexity': 0.25
        }

    def analyze_ui_size(self, html_content, screenshot_path=None):
        """
        分析UI尺寸复杂度
        考虑: 页面内容长度、元素数量、嵌套深度
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. HTML内容长度
        content_length = len(html_content)

        # 2. 总元素数量
        total_elements = len(soup.find_all())

        # 3. 最大嵌套深度
        def get_max_depth(element, current_depth=0):
            if not element.children:
                return current_depth
            max_child_depth = current_depth
            for child in element.children:
                if hasattr(child, 'children'):
                    child_depth = get_max_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            return max_child_depth

        max_depth = get_max_depth(soup)

        # 4. 如果有截图，分析图像尺寸
        image_complexity = 0
        if screenshot_path:
            try:
                img = cv2.imread(screenshot_path)
                if img is not None:
                    height, width = img.shape[:2]
                    image_complexity = (width * height) / 1000000  # 标准化到百万像素
            except:
                pass

        # 综合评分 (0-100)
        size_score = min(100, (
                (content_length / 1000) * 0.3 +
                (total_elements / 10) * 0.3 +
                (max_depth * 5) * 0.2 +
                (image_complexity * 10) * 0.2
        ))

        return {
            'score': size_score,
            'details': {
                'content_length': content_length,
                'total_elements': total_elements,
                'max_depth': max_depth,
                'image_complexity': image_complexity
            }
        }

    def analyze_ui_elements(self, html_content):
        """
        分析UI元素复杂度
        考虑: 交互元素数量、元素类型多样性、表单复杂度
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. 交互元素统计
        interactive_elements = {
            'buttons': len(soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])),
            'links': len(soup.find_all('a')),
            'inputs': len(soup.find_all('input')),
            'selects': len(soup.find_all('select')),
            'textareas': len(soup.find_all('textarea')),
            'forms': len(soup.find_all('form'))
        }

        # 2. 所有元素类型统计
        all_elements = soup.find_all()
        element_types = Counter([elem.name for elem in all_elements])
        type_diversity = len(element_types)

        # 3. 特殊元素
        special_elements = {
            'tables': len(soup.find_all('table')),
            'lists': len(soup.find_all(['ul', 'ol'])),
            'media': len(soup.find_all(['img', 'video', 'audio', 'canvas', 'svg'])),
            'scripts': len(soup.find_all('script'))
        }

        # 4. 表单复杂度
        forms = soup.find_all('form')
        form_complexity = 0
        for form in forms:
            form_inputs = len(form.find_all(['input', 'select', 'textarea']))
            form_complexity += form_inputs

        # 综合评分
        total_interactive = sum(interactive_elements.values())
        total_special = sum(special_elements.values())

        elements_score = min(100, (
                (total_interactive * 2) * 0.4 +
                (type_diversity * 1.5) * 0.3 +
                (total_special * 1.5) * 0.2 +
                (form_complexity * 1) * 0.1
        ))

        return {
            'score': elements_score,
            'details': {
                'interactive_elements': interactive_elements,
                'type_diversity': type_diversity,
                'special_elements': special_elements,
                'form_complexity': form_complexity
            }
        }

    def analyze_color_variety(self, screenshot_path, html_content=None):
        """
        分析颜色多样性
        主要从截图中提取，HTML作为辅助
        """
        if not screenshot_path:
            return {'score': 0, 'details': {'error': 'No screenshot provided'}}

        try:
            # 读取图像
            img = cv2.imread(screenshot_path)
            if img is None:
                return {'score': 0, 'details': {'error': 'Could not load image'}}

            # 转换到RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 1. 颜色直方图分析
            hist_r = cv2.calcHist([img_rgb], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img_rgb], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([img_rgb], [2], None, [256], [0, 256])

            # 2. 主要颜色提取 (K-means聚类)
            pixels = img_rgb.reshape(-1, 3)
            # 随机采样以提高性能
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]

            # 简化的颜色聚类
            unique_colors = np.unique(pixels.reshape(-1, pixels.shape[-1]), axis=0)
            n_colors = min(len(unique_colors), 50)  # 限制最大颜色数

            # 3. 颜色分布熵
            pixel_counts = Counter(map(tuple, pixels))
            total_pixels = len(pixels)
            entropy = -sum((count / total_pixels) * math.log2(count / total_pixels)
                           for count in pixel_counts.values())

            # 4. 颜色对比度
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            contrast = gray.std()

            # 5. 从HTML提取CSS颜色信息（如果提供）
            css_colors = 0
            if html_content:
                # 提取style属性和CSS中的颜色
                color_patterns = [
                    r'color:\s*#[0-9a-fA-F]{3,6}',
                    r'background-color:\s*#[0-9a-fA-F]{3,6}',
                    r'border-color:\s*#[0-9a-fA-F]{3,6}',
                    r'color:\s*rgb\([^)]+\)',
                    r'background-color:\s*rgb\([^)]+\)'
                ]
                for pattern in color_patterns:
                    css_colors += len(re.findall(pattern, html_content, re.IGNORECASE))

            # 综合评分
            color_score = min(100, (
                    (n_colors / 50 * 100) * 0.3 +
                    (min(entropy / 10, 1) * 100) * 0.3 +
                    (min(contrast / 100, 1) * 100) * 0.3 +
                    (min(css_colors / 20, 1) * 100) * 0.1
            ))

            return {
                'score': color_score,
                'details': {
                    'unique_colors': n_colors,
                    'color_entropy': entropy,
                    'contrast': contrast,
                    'css_colors': css_colors
                }
            }

        except Exception as e:
            return {'score': 0, 'details': {'error': str(e)}}

    def analyze_layout_complexity(self, html_content, screenshot_path=None):
        """
        分析布局复杂度
        考虑: CSS复杂度、布局方法、响应式设计、定位方式
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. CSS分析
        css_complexity = 0

        # 提取所有style标签和属性
        style_tags = soup.find_all('style')
        style_attrs = soup.find_all(attrs={'style': True})

        css_content = ' '.join([tag.get_text() for tag in style_tags])
        inline_styles = ' '.join([elem.get('style', '') for elem in style_attrs])
        all_css = css_content + ' ' + inline_styles

        # CSS属性复杂度指标
        layout_properties = [
            'display', 'position', 'float', 'flex', 'grid', 'transform',
            'margin', 'padding', 'width', 'height', 'top', 'left', 'right', 'bottom'
        ]

        for prop in layout_properties:
            css_complexity += len(re.findall(rf'{prop}\s*:', all_css, re.IGNORECASE))

        # 2. 布局方法检测
        layout_methods = {
            'flexbox': len(re.findall(r'display\s*:\s*flex', all_css, re.IGNORECASE)),
            'grid': len(re.findall(r'display\s*:\s*grid', all_css, re.IGNORECASE)),
            'float': len(re.findall(r'float\s*:', all_css, re.IGNORECASE)),
            'absolute': len(re.findall(r'position\s*:\s*absolute', all_css, re.IGNORECASE)),
            'fixed': len(re.findall(r'position\s*:\s*fixed', all_css, re.IGNORECASE))
        }

        # 3. 响应式设计检测
        responsive_indicators = [
            len(re.findall(r'@media', all_css, re.IGNORECASE)),
            len(re.findall(r'viewport', html_content, re.IGNORECASE)),
            len(re.findall(r'%|vw|vh|em|rem', all_css)),
        ]

        # 4. 嵌套复杂度
        nested_divs = 0
        for div in soup.find_all('div'):
            nested_divs += len(div.find_all('div'))

        # 5. 表格布局
        table_complexity = 0
        for table in soup.find_all('table'):
            rows = len(table.find_all('tr'))
            cols = len(table.find_all(['td', 'th']))
            table_complexity += rows * cols

        # 6. 如果有截图，进行视觉布局分析
        visual_complexity = 0
        if screenshot_path:
            try:
                img = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # 边缘检测来估计布局复杂度
                    edges = cv2.Canny(img, 50, 150)
                    visual_complexity = np.sum(edges > 0) / (img.shape[0] * img.shape[1])
            except:
                pass

        # 综合评分
        layout_score = min(100, (
                (css_complexity / 50) * 0.25 +
                (sum(layout_methods.values()) / 10) * 0.2 +
                (sum(responsive_indicators) / 10) * 0.15 +
                (nested_divs / 20) * 0.15 +
                (table_complexity / 100) * 0.1 +
                (visual_complexity * 100) * 0.15
        ))

        return {
            'score': layout_score,
            'details': {
                'css_complexity': css_complexity,
                'layout_methods': layout_methods,
                'responsive_indicators': sum(responsive_indicators),
                'nested_divs': nested_divs,
                'table_complexity': table_complexity,
                'visual_complexity': visual_complexity
            }
        }

    def calculate_difficulty(self, html_content, screenshot_path=None):
        """
        计算网页总体难度
        """
        # 分析各项指标
        ui_size = self.analyze_ui_size(html_content, screenshot_path)
        ui_elements = self.analyze_ui_elements(html_content)
        color_variety = self.analyze_color_variety(screenshot_path, html_content)
        layout_complexity = self.analyze_layout_complexity(html_content, screenshot_path)

        # 计算加权总分
        total_score = (
                ui_size['score'] * self.weights['ui_size'] +
                ui_elements['score'] * self.weights['ui_elements'] +
                color_variety['score'] * self.weights['color_variety'] +
                layout_complexity['score'] * self.weights['layout_complexity']
        )

        # 确定难度等级
        if total_score < 20:
            difficulty_level = "Very Easy"
        elif total_score < 40:
            difficulty_level = "Easy"
        elif total_score < 60:
            difficulty_level = "Medium"
        elif total_score < 80:
            difficulty_level = "Hard"
        else:
            difficulty_level = "Very Hard"

        return {
            'total_score': round(total_score, 2),
            'difficulty_level': difficulty_level,
            'component_scores': {
                'ui_size': round(ui_size['score'], 2),
                'ui_elements': round(ui_elements['score'], 2),
                'color_variety': round(color_variety['score'], 2),
                'layout_complexity': round(layout_complexity['score'], 2)
            },
            'detailed_analysis': {
                'ui_size': ui_size['details'],
                'ui_elements': ui_elements['details'],
                'color_variety': color_variety['details'],
                'layout_complexity': layout_complexity['details']
            },
            'weights_used': self.weights
        }


# 使用示例
def cal_webpage_difficulty(html_file, png_file):
    # 创建分析器实例
    analyzer = WebpageDifficultyAnalyzer()

    # png_file = f"../../../data/DesignGeneration/vue/1/1.png"
    # html_file = f"../../../data/DesignGeneration/vue/1/1.html"

    with open(html_file, "r") as f_html:
        html_content = f_html.read()

    # 分析网页难度
    result = analyzer.calculate_difficulty(
        html_content=html_content,
        screenshot_path=png_file  # 可选：提供截图路径
    )

    return result['total_score']

    # # 输出结果
    # print("=== 网页难度分析结果 ===")
    # print(f"总分: {result['total_score']}/100")
    # print(f"难度等级: {result['difficulty_level']}")
    # print("\n各项得分:")
    # for component, score in result['component_scores'].items():
    #     print(f"  {component}: {score}")
    #
    # print("\n详细分析:")
    # for component, details in result['detailed_analysis'].items():
    #     print(f"\n{component}:")
    #     for key, value in details.items():
    #         print(f"  {key}: {value}")
    #
#
# if __name__ == "__main__":
#     main()