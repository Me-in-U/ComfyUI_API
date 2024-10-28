import os
from rembg import remove
from PIL import Image
import io


def remove_background(input_path, output_path):
    """이미지에서 배경을 제거하고 결과를 저장하는 함수."""
    try:
        # 이미지를 PIL로 직접 열지 않고, 바이너리 형태로 rembg에 전달
        with open(input_path, 'rb') as file:
            input_image = file.read()

        # 배경 제거
        output_image_data = remove(input_image)

        # 결과 데이터를 PIL 이미지 객체로 변환
        output_image = Image.open(io.BytesIO(output_image_data))

        # 결과 이미지가 RGBA인 경우 RGB로 변환
        if output_image.mode == 'RGBA':
            output_image = output_image.convert('RGB')

        # 결과 이미지 저장
        output_image.save(output_path)
        print(f"Processed and saved {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

    return output_path


# 이미지가 저장된 폴더 경로 및 결과 저장 폴더 설정
input_directory = "E:\\Languages\\Apache24\\ComfyUI_API\\output\\ND"
output_directory = "E:\\Languages\\Apache24\\ComfyUI_API\\output\\NDRBG"

# 결과 저장 폴더 생성
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# 폴더 내 모든 파일 처리
for filename in os.listdir(input_directory):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename)

        if os.path.exists(output_path):
            # print(f"Skipping {filename}, already processed.")
            continue

        # 배경 제거 함수 호출
        remove_background(input_path, output_path)
