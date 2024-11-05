from api.api_helpers import generate_image_by_image_image
from utils.helpers.randomize_seed import generate_random_int
from utils.actions.getImagePath import read_image_paths_from_temp_file
import json


def vton_dress(workflow, input_path1, input_path2, save_previews=False):
    prompt = json.loads(workflow)

    # generate_random_15_digit_number로 랜덤 시드 생성
    k_sampler_id = [key for key, value in prompt.items(
    ) if value['class_type'] == 'IDM_VTON_NN' and value['_meta']['title'] == 'IDM-VTON (diffusers)'][0]
    prompt[k_sampler_id]['inputs']['seed'] = generate_random_int()

    # human_image 이미지 path 변경
    image_loader1 = [key for key, value in prompt.items(
    ) if value['class_type'] == 'LoadImage' and value['_meta']['title'] == 'human_image'][0]
    prompt[image_loader1]['inputs']['image'] = input_path1

    # clothes_image 이미지 path 변경
    image_loader2 = [key for key, value in prompt.items(
    ) if value['class_type'] == 'LoadImage' and value['_meta']['title'] == 'clothes_image'][0]
    prompt[image_loader2]['inputs']['image'] = input_path2

    filename1 = input_path1.split('\\')[-1]
    filename2 = input_path2.split('\\')[-1]

    # 이미지 생성 함수 호출
    generate_image_by_image_image(
        prompt, './output/', input_path1, filename1, input_path2, filename2, save_previews)

    # tempImage.txt 파일에서 이미지 경로 읽기
    return read_image_paths_from_temp_file()[0]
