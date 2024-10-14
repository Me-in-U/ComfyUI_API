from api.api_helpers import generate_image_by_prompt, generate_image_by_prompt_and_image
from utils.helpers.randomize_seed import generate_random_15_digit_number
from api.open_websocket import open_websocket_connection
import json


def human_plus_dress(workflow, input_path, positive_prompt, negative_prompt, save_previews=False):
    prompt = json.loads(workflow)

    # Positive Prompt 변경
    positive_prompt_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'CLIPTextEncode' and value['_meta']['title'] == 'Positive Prompt'][0]
    prompt[positive_prompt_id]['inputs']['text'] = positive_prompt

    negative_prompt_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'CLIPTextEncode' and value['_meta']['title'] == 'Negative Prompt'][0]
    prompt[negative_prompt_id]['inputs']['text'] = negative_prompt

    # generate_random_15_digit_number로 랜덤 시드 생성
    k_sampler_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'KSampler'][0]
    prompt[k_sampler_id]['inputs']['seed'] = generate_random_15_digit_number()
    # print("seed updated to: ", prompt[k_sampler_id]['inputs']['seed'])

    # input_img1 이미지 path 변경
    image_loader = [key for key, value in prompt.items(
    ) if value['class_type'] == 'LoadImage' and value['_meta']['title'] == 'input_img1'][0]
    prompt[image_loader]['inputs']['image'] = input_path
    # print(prompt[image_loader]['inputs']['image'])

    # input_img2 이미지 path 변경
    # image_loader = [key for key, value in prompt.items(
    # ) if value['class_type'] == 'LoadImage' and value['_meta']['title'] == 'input_img2'][0]
    # prompt[image_loader]['inputs']['image'] = input_path

    filename = input_path.split('\\')[-1]
    # print(input_path.split('\\')[-1])

    # 이미지 생성 함수 호출
    # generate_image_by_prompt(prompt, './output/', save_previews)
    generate_image_by_prompt_and_image(
        prompt, './output/', input_path, filename, save_previews)

    # tempImage.txt 파일에서 이미지 경로 읽기
    return read_image_paths_from_temp_file()


def read_image_paths_from_temp_file():
    image_paths = []
    try:
        with open('tempImage.txt', 'r') as file:
            image_paths = file.readlines()
        image_paths = [path.strip() for path in image_paths]  # 공백 및 개행 제거
    except FileNotFoundError:
        print("tempImage.txt file not found.")
    return image_paths
