import os
import threading
from rembg import remove
from PIL import Image
import io


def remove_background(input_path, output_path):
    """이미지에서 배경을 제거하고 결과를 저장하는 함수."""
    try:
        with open(input_path, 'rb') as file:
            input_image = file.read()

        output_image_data = remove(input_image)
        output_image = Image.open(io.BytesIO(output_image_data))

        if output_image.mode == 'RGBA':
            output_image = output_image.convert('RGB')

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
    input_directory = "E:\\Languages\\Apache24\\ComfyUI_API\\output\\ND"
    output_directory = "E:\\Languages\\Apache24\\ComfyUI_API\\output\\NDRBG"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    threads = []
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            thread = threading.Thread(target=process_image, args=(
                filename, input_directory, output_directory))
            threads.append(thread)
            thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
