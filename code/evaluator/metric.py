import cv2
import difflib
import torch
from PIL import Image
from torch.nn.functional import cosine_similarity
import clip
import numpy as np
from skimage.metrics import structural_similarity as ssim
from metrci_utils import *
import base64
import retry
from openai import OpenAI

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def diff_files(file1_path, file2_path):
    """
    比较两个文件并输出差异，包括对应原始文件中的行号

    Args:
        file1_path: 第一个文件的路径
        file2_path: 第二个文件的路径
    """
    line_numbers = []
    modified_code = []
    try:
        # 读取两个文件的内容
        with open(file1_path, 'r', encoding='utf-8') as f1:
            file1_lines = f1.readlines()

        with open(file2_path, 'r', encoding='utf-8') as f2:
            file2_lines = f2.readlines()

        # 移除行尾的换行符，便于比较
        file1_lines = [line.rstrip('\n') for line in file1_lines]
        file2_lines = [line.rstrip('\n') for line in file2_lines]

        # 使用SequenceMatcher获取详细的差异
        matcher = difflib.SequenceMatcher(None, file1_lines, file2_lines)

        # print(f"比较文件 '{file1_path}' 和 '{file2_path}' 的差异:")
        # print("-" * 60)

        has_diff = False
        # 输出差异块
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue  # 跳过相同的部分

            # for line_number in range(j1, j2+1):
            #     line_numbers.append(line_number)
            #     modified_code.append(file2_lines[line_number])

            has_diff = True

            if tag == 'replace':
                # print(f"\n修改: 文件1的第 {i1 + 1}-{i2} 行 被修改为 文件2的第 {j1 + 1}-{j2} 行")
                # print("原始内容:")
                # for i in range(i1, i2):
                #     print(f"  文件1 行 {i + 1}: {file1_lines[i]}")
                # print("修改后内容:")
                for j in range(j1, j2):
                    # print(f"  文件2 行 {j + 1}: {file2_lines[j]}")
                    line_numbers.append(j + 1)
                    modified_code.append(file2_lines[j])

            elif tag == 'delete':
                # print(f"\n删除: 文件1的第 {i1 + 1}-{i2} 行在文件2中被删除")
                # print("删除内容:")
                for i in range(i1, i2):
                    line_numbers
                    # print(f"  文件1 行 {i + 1}: {file1_lines[i]}")


            elif tag == 'insert':
                # print(f"\n插入: 在文件2的第 {j1 + 1}-{j2} 行新增了内容")
                # print("新增内容:")
                for j in range(j1, j2):
                    # print(f"  文件2 行 {j + 1}: {file2_lines[j]}")
                    line_numbers.append(j + 1)
                    modified_code.append(file2_lines[j])

            # print("-" * 40)

        # if not has_diff:
        #     print("两个文件内容完全相同。")

        # print(line_numbers)
        #
        # print(modified_code)

    except FileNotFoundError as e:
        print(f"错误: 文件不存在 - {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        return line_numbers, modified_code


def code_similarity(src_code, reference_code, generated_code):
    # src_code = src_code.split("\n")
    # reference_code = reference_code.split("\n")

    # diff = difflib.unified_diff(src_code, reference_code)

    with open("code1", "w") as fs:
        fs.write(src_code)

    with open("code2", "w") as fs:
        fs.write(reference_code)

    with open("code3", "w") as fs:
        fs.write(generated_code)

    # git_diff_lines(file1="code1", file2="code2")
    #
    # git_diff_lines(file1="code1", file2="code3")

    line_numbers_ref, modified_code_ref = diff_files(file1_path="code1", file2_path="code2")

    line_numbers_generated, modified_code_generated = diff_files(file1_path="code1", file2_path="code3")

    line_numbers_ref = set(line_numbers_ref)
    line_numbers_generated = set(line_numbers_generated)

    # print(line_numbers_ref)
    # print(line_numbers_generated)
    # print(line_numbers_ref.intersection(line_numbers_generated))

    interaction_line_numbers = line_numbers_ref.intersection(line_numbers_generated)
    #
    union_line_numbers = line_numbers_ref.union(line_numbers_generated)

    if len(union_line_numbers) == 0:
        return 1
        # if len() == 0:
        #     return 1
        # else:
        #     return 0
    else:
        jaccard = len(interaction_line_numbers) / len(union_line_numbers)
        return jaccard

    # return jaccard(line_numbers_ref, line_numbers_generated)

    # print(diff)
    # print(src_code)
    # print(reference_code)


def mae_score(img1, img2):
    """mean absolute error, it is a pixel-based metric"""
    img1, img2 = process_imgs(img1, img2, 512)
    # max_mae = np.mean(np.maximum(img1, 255 - img1))
    mae = np.mean(np.abs(img1 - img2))
    # return {"mae": mae, "normalized_mae": 1 - mae / max_mae}
    return mae


def process_imgs(image1, image2, max_size):
    # Get the original sizes
    width1, height1 = image1.size
    width2, height2 = image2.size

    # Determine the new dimensions (max of both images' width and height)
    new_width = max(width1, width2)
    new_height = max(height1, height2)

    # Pad images to the new dimensions with random values
    def pad_image(image, new_width, new_height):
        # Create a random padded background with the new dimensions
        random_padding = np.random.randint(0, 256, (new_height, new_width, 3), dtype=np.uint8)
        padded_image = Image.fromarray(random_padding)

        # Paste the original image onto the padded background (placing in the top-left corner)
        padded_image.paste(image, (0, 0))

        return padded_image

    padded_image1 = pad_image(image1, new_width, new_height)
    padded_image2 = pad_image(image2, new_width, new_height)

    # Calculate the aspect ratio for resizing to the max size
    aspect_ratio = min(max_size / new_width, max_size / new_height)
    new_size = (int(new_width * aspect_ratio), int(new_height * aspect_ratio))

    # Resize the padded images to the specified max size
    resized_image1 = padded_image1.resize(new_size, Image.LANCZOS)
    resized_image2 = padded_image2.resize(new_size, Image.LANCZOS)

    # resized_image1.show()
    # resized_image2.show()

    # Convert the images to numpy arrays with dtype int16
    array1 = np.array(resized_image1).astype(np.int16)
    array2 = np.array(resized_image2).astype(np.int16)

    return array1, array2


def clip_similarity(image_path1, image_path2):
    # Load the CLIP model and processor
    # Load and preprocess the images
    if isinstance(image_path1, str) and isinstance(image_path2, str):
        img1 = Image.open(image_path1)
        img2 = Image.open(image_path2)
    else:
        img1 = image_path1
        img2 = image_path2
    # Load and preprocess the images
    img1 = preprocess(img1).unsqueeze(0).to(device)
    img2 = preprocess(img2).unsqueeze(0).to(device)

    # Extract features using CLIP
    with torch.no_grad():
        features1 = model.encode_image(img1)
        features2 = model.encode_image(img2)

    # Normalize the features
    features1 = features1 / features1.norm(p=2, dim=-1, keepdim=True)
    features2 = features2 / features2.norm(p=2, dim=-1, keepdim=True)

    # Compute cosine similarity
    similarity = cosine_similarity(features1, features2)

    # Output the similarity score
    # print(f"Similarity: {similarity.item()}")
    return similarity.item()


def ssim_similarity(image_path1, image_path2):
    image1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)
    image2_resized = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    score, diff = ssim(image1, image2_resized, full=True)
    return score


# encoding image for gemini
def gemini_encode_image(image_path):
    return Image.open(image_path)


# encoding image for gpt, claude, qwen, mistral, llama
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def llm_edit_judge(original_image, edited_image, instruction):
    # input two images and instruction, using LLM to judge whether the instruction is implemented

    original_image = encode_image(original_image)
    edited_image = encode_image(edited_image)
    prompt = f"The edit instruction is {instruction}"

    response = gpt_edit_judge(model_name="gpt-4o-2024-11-20", original_image=original_image, edited_image=edited_image,
                              prompt=prompt)
    return response


def llm_repair_judge(original_image, repaired_image, reference_image, issues):
    original_image = encode_image(original_image)
    repaired_image = encode_image(repaired_image)
    reference_image = encode_image(reference_image)

    prompt = f"""
    The first image is the before-fix UI screenshot, and the issues in the original image: {issues}.
    The second image is after-fix UI screenshot.
    The third image is the ground-truth fixed UI screenshot.
    """

    response = gpt_repair_judge(model_name="gpt-4o-2024-11-20", original_image=original_image,
                                repaired_image=repaired_image, reference_image=reference_image,
                                prompt=prompt)


    return response


with open(key_path, "r") as fs:
    keys = json.loads(fs.read())

EDIT_JUDGE_SYSTEM_PROMPT = """
## Task Description
You are evaluating whether an edited UI screenshot properly implements a user's instructions for modifications. The user provides you with:
1. The original UI screenshot
2. The user's instructions for modifications
3. The edited UI screenshot after modifications

## Evaluation Framework
Score the edited UI on a scale of 1-10 based on how well it implements the user's instructions, where:
- 0-3: Poor implementation (significant discrepancies or missing elements)
- 4-6: Partial implementation (some instructions followed, others missed)
- 7-8: Good implementation (most instructions followed with minor issues)
- 9-10: Excellent implementation (instructions followed completely and coherently)

## Evaluation Criteria
Analyze and score the following aspects:

1. Instruction Compliance (0-4 points)
- Were all specific elements mentioned in the instructions modified?
- Were the modifications made exactly as specified?
- Were any requested elements missed or ignored?

2. Visual Quality and Consistency (0-3 points)
- Do the modifications maintain the original design language?
- Is the overall visual hierarchy preserved or improved?
- Are colors, fonts, and spacing consistent with the original design where not explicitly changed?

3. Functional Integrity (0-3 points)
- Do the modifications preserve the apparent functionality of the UI?
- Are interaction elements (buttons, forms, menus) still clearly usable?
- Would the modified UI likely work as intended from a user perspective?

## Output
Please provide the following information and combine them into json format:

1. Overall Score: A numerical score from 1-10

2. Detailed Assessment:
   - List each instruction and whether it was implemented correctly
   - Note any discrepancies between instructions and implementation
   - Highlight any quality issues in the implementation

3. Reasoning:
   - Explain your scoring rationale
   - Describe specific elements that influenced your score


## Example Response

```json
{
"score":7,
"Detailed Assessment": "- Instruction: 'Change button color to blue' ✓ Implemented correctly\n- Instruction: 'Move navigation menu to the left side' ✓ Implemented correctly\n- Instruction: 'Add search bar at the top' ✗ Search bar was added but placed at the bottom\n- Instruction: 'Make font size larger for headings' ∼ Font size increased but inconsistently",
"Reasoning": "The edited UI successfully implemented 2 out of 4 instructions completely. The search bar placement doesn't match instructions, and the heading font size changes were inconsistent across different sections. The modifications maintain the original design language and the UI appears functionally sound."
}
```
"""


@retry.retry(tries=3, delay=2)
def gpt_edit_judge(model_name, original_image, edited_image, prompt):
    openai_client = OpenAI(
        api_key=keys["gpt"],
        base_url="https://openkey.cloud/v1"
    )

    response = openai_client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": EDIT_JUDGE_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{original_image}",
                            "detail": "high"
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{edited_image}",
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
        max_tokens=4096,
        temperature=1,
        seed=42
    )

    print(response)
    response = response.choices[0].message.content.strip()
    # response = extract_json_blocks(response)[0]
    # response = cleanup_response(response)

    return response


REPAIR_JUDGE_SYSTEM_PROMPT = """
## Task Description
You are evaluating the effectiveness of a UI fix task. The user provides you with:
1. A before-fix UI screenshot (with red boxes marking problem areas)
2. An after-fix UI screenshot (the actual fix result to be evaluated)
3. A ground-truth fixed UI screenshot (the reference/ideal fix)
4. The specific UI issue type description

Please determine whether the actual fixed image successfully resolves the problems in the red-boxed areas and how well it matches the ground-truth reference.

## Evaluation Framework
Score the UI fix on a scale of 1-10 based on how well it resolves the identified problems and matches the ground-truth reference, where:
- 1-3: Fix failed (problem unresolved, significant deviation from ground-truth)
- 4-6: Partial fix (problem partially resolved, moderate alignment with ground-truth)
- 7-8: Good fix (problem effectively resolved, close alignment with ground-truth)
- 9-10: Excellent fix (problem completely resolved, matches ground-truth closely)

## Evaluation Criteria
Analyze and score the following aspects:

1. Problem Resolution (0-3 points)
- Were the red-boxed problem areas addressed?
- Does the fix directly target the specified UI issue type?
- Is the original problem completely eliminated?

2. Ground-Truth Alignment (0-4 points)
- How closely does the actual fix match the ground-truth reference?
- Are the key visual elements (layout, colors, typography) consistent with the reference?
- Does the fix approach align with the reference solution method?

3. Overall Quality (0-3 points)
- Does the fixed area look natural and harmonious?
- Is the overall page layout and visual balance maintained?
- Are new visual problems introduced?

## Common UI Issue Types Reference
Based on the provided issue type, focus on these aspects:
- occlusion: Elements are hidden or partially covered by other elements, making content inaccessible or invisible to users. This includes overlapping components, modal dialogs blocking content, or elements positioned behind others.
- crowding: Too many elements are packed into a small space without adequate spacing, making the interface feel cluttered and difficult to navigate. This affects readability and user experience.
- text overlap: Text content overlaps with other text or UI elements, making it unreadable or causing visual confusion. This often occurs due to improper positioning, z-index issues, or responsive design problems.
- alignment: Elements are not properly aligned with each other or the overall layout grid, creating a disorganized and unprofessional appearance. This includes misaligned text, buttons, images, or containers.
- color and contrast: Poor color choices that affect readability or accessibility, including insufficient contrast between text and background, or color combinations that are difficult for users with visual impairments to distinguish.
- overflow: Content extends beyond its intended container boundaries, causing horizontal scrollbars, cut-off text, or elements appearing outside their designated areas.

## Output
Please provide the following information and combine them into json format:

1. Overall Score: A numerical score from 1-10

2. Problem Analysis:
   - Describe the original problem identified in the red-boxed area
   - Assess the severity of the original problem
   - Evaluate whether the problem was resolved in the actual fix

3. Ground-Truth Comparison:
   - Compare the actual fix with the ground-truth reference
   - Note similarities and differences in the fix approach
   - Assess how well the actual fix aligns with the reference solution

4. Fix Assessment:
   - Analyze the effectiveness of the fix method used
   - Note any improvements made to the problematic area
   - Identify any remaining issues or new problems introduced

5. Reasoning:
   - Explain your scoring rationale for each evaluation criteria
   - Describe specific elements that influenced your score

## Example Response

```json
{
"score": 8,
"Problem Analysis": "Original problem: Button text was truncated on the right side, showing only partial text 'Submit Fo...' instead of 'Submit Form'. Problem severity: Moderate - affects usability but doesn't break core functionality. Resolution status: Completely resolved - button now displays full text clearly.",
"Ground-Truth Comparison": "The ground-truth reference shows the button expanded to accommodate full text with proper padding. The actual fix closely matches this approach: both solutions expand button width, maintain consistent styling, and preserve button functionality. Minor difference: actual fix uses slightly less horizontal padding than the reference.",
"Fix Assessment": "Fix method: Increased button width to accommodate full text - matches the reference approach perfectly. Improvements: Button text now displays completely, improved readability and user experience, maintains visual consistency with other UI elements. Remaining issues: None identified - fix appears complete and effective.",
"Reasoning": "Problem Resolution (3/3): Text truncation issue completely resolved, matching the reference solution. Ground-Truth Alignment (3/4): Very close match to reference but with minor padding differences. Overall Quality (2/3): Excellent visual result but slightly tighter spacing than ideal reference."
}
```
"""


@retry.retry(tries=3, delay=2)
def gpt_repair_judge(model_name, original_image, repaired_image, reference_image, prompt):
    openai_client = OpenAI(
        api_key=keys["gpt"],
        base_url="https://openkey.cloud/v1"
    )

    response = openai_client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": REPAIR_JUDGE_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{original_image}",
                            "detail": "high"
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{repaired_image}",
                            "detail": "high"
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{reference_image}",
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
        max_tokens=4096,
        temperature=1,
        seed=42
    )

    print(response)
    response = response.choices[0].message.content.strip()
    # response = extract_json_blocks(response)[0]
    # response = cleanup_response(response)

    return response
