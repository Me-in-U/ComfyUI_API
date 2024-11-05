import io
import os
import threading

from PIL import Image
from rembg import remove

BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\output"
INPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "ND")
OUTPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "NDRBG")


def remove_background(input_path, output_path):
    """이미지에서 배경을 제거하고 결과를 저장하는 함수."""
    try:
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


def process_image(filename, input_directory, output_directory):
    input_path = os.path.join(input_directory, filename)
    output_path = os.path.join(output_directory, filename)

    if os.path.exists(output_path):
        # print(f"Skipping {filename}, already processed.")
        pass
    else:
        remove_background(input_path, output_path)


def main():
    if not os.path.exists(INPUT_DIRECTORY):
        os.makedirs(INPUT_DIRECTORY)
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

    threads = []
    for filename in os.listdir(INPUT_DIRECTORY):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            thread = threading.Thread(target=process_image, args=(
                filename, INPUT_DIRECTORY, OUTPUT_DIRECTORY))
            threads.append(thread)
            thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
