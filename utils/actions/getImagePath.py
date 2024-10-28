def read_image_paths_from_temp_file():
    image_paths = []
    try:
        with open('tempImage.txt', 'r') as file:
            image_paths = file.readlines()
        image_paths = [path.strip() for path in image_paths]  # 공백 및 개행 제거
    except FileNotFoundError:
        print("tempImage.txt file not found.")
    return image_paths
