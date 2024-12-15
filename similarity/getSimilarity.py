# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import base64
import os
import tempfile

import numpy as np
from scipy.spatial import distance
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image

DATA_BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\output"
DATA_ND_DIRECTORY = os.path.join(DATA_BASE_DIRECTORY, "ND")
DATA_NPY_DIRECTORY = os.path.join(DATA_BASE_DIRECTORY, "NDNPY")


# 이미지를 Base64로 인코딩하는 함수
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def load_and_preprocess_img(path):
    img = image.load_img(path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x


def extract_features(img_path, model):
    img = load_and_preprocess_img(img_path)
    features = model.predict(img)
    return features.flatten()


def extract_and_save_features(img_path, features_path, model):
    if not os.path.exists(features_path):
        features = extract_features(img_path, model)
        np.save(features_path, features)
    else:
        features = np.load(features_path)
    return features


def dataset_features_to_dictionary(input_directory, output_directory, model):
    features_dict = {}
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for img_name in os.listdir(input_directory):
        if img_name.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):  # 이미지 파일 확장자 확인
            img_path = os.path.join(input_directory, img_name)
            features_path = os.path.join(
                output_directory, os.path.splitext(img_name)[0] + ".npy"
            )
            features_dict[img_path] = extract_and_save_features(
                img_path, features_path, model
            )
    return features_dict


def find_similar_images(target_features, features_dict, top_n=5):
    similarities = {}
    for path, features in features_dict.items():
        if path.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):  # 다시 한번 이미지 파일만 처리
            sim = 1 - distance.cosine(target_features, features)
            similarities[path] = sim
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    return sorted_similarities[:top_n]


def return_images(image_bytes, top_n):
    # 모델 로드
    base_model = VGG16(weights="imagenet")
    model = Model(inputs=base_model.input, outputs=base_model.get_layer("fc2").output)

    # 이미지 입력
    # 바이트 데이터로부터 이미지 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file_path = tmp_file.name

    # 입력 이미지의 features 만들기
    temp_features = extract_and_save_features(
        tmp_file_path, tmp_file_path + ".npy", model
    )  # 임시 파일의 경로를 사용

    # 데이터셋에서 features 딕셔너리 만들기
    features_dict = dataset_features_to_dictionary(
        DATA_ND_DIRECTORY, DATA_NPY_DIRECTORY, model
    )

    # 유사 이미지 찾기
    similar_images = find_similar_images(temp_features, features_dict, top_n)

    # 임시 파일 삭제
    os.remove(tmp_file_path)

    base_model = None
    model = None

    return similar_images


def return_images2(created_image_path, top_n):
    # 모델 로드
    base_model = VGG16(weights="imagenet")
    model = Model(inputs=base_model.input, outputs=base_model.get_layer("fc2").output)

    # 입력 이미지의 features 만들기
    temp_features = extract_and_save_features(
        created_image_path, created_image_path + ".npy", model
    )  # 임시 파일의 경로를 사용

    # 데이터셋에서 features 딕셔너리 만들기
    features_dict = dataset_features_to_dictionary(
        DATA_ND_DIRECTORY, DATA_NPY_DIRECTORY, model
    )

    # 유사 이미지 찾기
    similar_images = find_similar_images(temp_features, features_dict, top_n)

    base_model = None
    model = None

    return similar_images


# def test_code():
#     INPUT_BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\similarity"
#     # 모델 로드
#     base_model = VGG16(weights="imagenet")
#     model = Model(inputs=base_model.input, outputs=base_model.get_layer("fc2").output)

#     # 입력 이미지
#     input_img_path = "E:\\ComfyUI_0.2.2\\ComfyUI\\output\\ND_00004_.png"
#     base_name = os.path.basename(input_img_path)

#     # 입력 이미지의 features 만들기
#     input_npy_path = os.path.join(
#         INPUT_BASE_DIRECTORY, f"{os.path.splitext(base_name)[0]}.npy"
#     )
#     target_features = extract_and_save_features(input_img_path, input_npy_path, model)

#     # 데이터셋에서 features 딕셔너리 만들기
#     features_dict = dataset_features_to_dictionary(
#         DATA_ND_DIRECTORY, DATA_NPY_DIRECTORY, model
#     )

#     # 유사 이미지 찾기
#     similar_images = find_similar_images(target_features, features_dict)

#     for img, sim in similar_images:
#         print(f"{img}: 유사도 = {sim}")


# test_code()
