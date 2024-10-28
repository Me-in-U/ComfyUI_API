import os
import numpy as np
from scipy.spatial import distance
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
# from rembg import remove
# from PIL import Image
# from removeBG import remove_background


INPUT_BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\input"
INPUT_RBG_DIRECTORY = os.path.join(INPUT_BASE_DIRECTORY, "inputRBG")
INPUT_NPY_DIRECTORY = os.path.join(INPUT_BASE_DIRECTORY, "inputNPY")

DATA_BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\output"
DATA_NPY_DIRECTORY = os.path.join(DATA_BASE_DIRECTORY, "NDNPY_origin")
DATA_RBG_DIRECTORY = os.path.join(DATA_BASE_DIRECTORY, "ND")
# DATA_RBG_DIRECTORY = os.path.join(INPUT_BASE_DIRECTORY, "NDRBG")

# VGG16 모델 로드
base_model = VGG16(weights='imagenet')
model = Model(inputs=base_model.input,
              outputs=base_model.get_layer('fc2').output)


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


def extract_features_from_directory(input_directory, output_directory, model):
    features_dict = {}
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for img_name in os.listdir(input_directory):
        if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):  # 이미지 파일 확장자 확인
            img_path = os.path.join(input_directory, img_name)
            features_file = os.path.join(
                output_directory, os.path.splitext(img_name)[0] + '.npy')
            if os.path.exists(features_file):
                features = np.load(features_file)
            else:
                features = extract_features(img_path, model)
                np.save(features_file, features)  # 특징 벡터를 파일로 저장
            features_dict[img_path] = features
    return features_dict


def extract_and_save_features(img_path, features_path, model):
    if not os.path.exists(features_path):
        features = extract_features(img_path, model)
        np.save(features_path, features)
    else:
        features = np.load(features_path)
    return features


def find_similar_images(target_features, features_dict, top_n=5):
    similarities = {}
    for path, features in features_dict.items():
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):  # 다시 한번 이미지 파일만 처리
            sim = 1 - distance.cosine(target_features, features)
            similarities[path] = sim
    sorted_similarities = sorted(
        similarities.items(), key=lambda x: x[1], reverse=True)
    return sorted_similarities[:top_n]


# Paths configuration
input_img_path = "E:\\Languages\\Apache24\\ComfyUI_API\\input\\search.pstatic.jpg"
base_name = os.path.basename(input_img_path)
if not os.path.exists(INPUT_RBG_DIRECTORY):
    os.makedirs(INPUT_RBG_DIRECTORY)
if not os.path.exists(INPUT_NPY_DIRECTORY):
    os.makedirs(INPUT_NPY_DIRECTORY)

# Remove background and save
input_rbg_path = os.path.join(INPUT_RBG_DIRECTORY, base_name)
# removeBG_path = remove_background(input_img_path, input_rbg_path)

# Extract features and save
input_npy_path = os.path.join(
    INPUT_NPY_DIRECTORY, f"{os.path.splitext(base_name)[0]}.npy")
# target_features = extract_and_save_features(
#     input_rbg_path, input_npy_path, model)
target_features = extract_and_save_features(
    input_img_path, input_npy_path, model)

# Load features from directory
features_dict = extract_features_from_directory(
    DATA_RBG_DIRECTORY, DATA_NPY_DIRECTORY, model)

# Find similar images
similar_images = find_similar_images(target_features, features_dict)

for img, sim in similar_images:
    print(f"{img}: 유사도 = {sim}")
