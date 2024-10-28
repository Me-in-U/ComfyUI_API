from api.api_helpers import generate_image_by_prompt
from utils.helpers.randomize_seed import generate_random_15_digit_number
from api.open_websocket import open_websocket_connection
import json
import shutil


def new_dress(workflow, positive_prompt, negative_prompt, save_previews=False):
    prompt = json.loads(workflow)

    # Positive Prompt 변경
    positive_prompt_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'CLIPTextEncode' and value['_meta']['title'] == 'Positive Prompt(NDI)'][0]
    prompt[positive_prompt_id]['inputs']['text'] = positive_prompt

    # Negative Prompt 변경
    negative_prompt_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'CLIPTextEncode' and value['_meta']['title'] == 'Negative Prompt(NDI)'][0]
    prompt[negative_prompt_id]['inputs']['text'] = negative_prompt

    # generate_random_15_digit_number로 랜덤 시드 생성
    k_sampler_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'KSampler' and value['_meta']['title'] == 'KSampler(NDI)'][0]
    prompt[k_sampler_id]['inputs']['seed'] = generate_random_15_digit_number()

    # 이미지 생성 함수 호출
    generate_image_by_prompt(
        prompt, './output/', save_previews)

    return_image_path = read_image_paths_from_temp_file()

    # 이미지를 다른 디렉토리에 복사
    destination_directory = "E:\\Languages\\Apache24\\ComfyUI_API\\output\\ND\\"  # 목적지 폴더 경로
    for path in return_image_path:
        try:
            shutil.copy(path, destination_directory)
            print(f"File {path} copied to {destination_directory}")
        except Exception as e:
            print(f"Error copying {path}: {str(e)}")

    # tempImage.txt 파일에서 이미지 경로 읽기
    return return_image_path


def read_image_paths_from_temp_file():
    image_paths = []
    try:
        with open('tempImage.txt', 'r') as file:
            image_paths = file.readlines()
        image_paths = [path.strip() for path in image_paths]  # 공백 및 개행 제거
    except FileNotFoundError:
        print("tempImage.txt file not found.")
    return image_paths
