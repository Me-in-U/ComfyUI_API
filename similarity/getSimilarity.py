from tensorflow.keras.models import Model
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
import os
import io
import numpy as np
from PIL import Image
from scipy.spatial import distance
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import base64
import tempfile
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template

INPUT_BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\input"
INPUT_NPY_DIRECTORY = os.path.join(INPUT_BASE_DIRECTORY, "inputNPY")

DATA_BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API\\output"
DATA_ND_DIRECTORY = os.path.join(DATA_BASE_DIRECTORY, "ND")
DATA_NPY_DIRECTORY = os.path.join(DATA_BASE_DIRECTORY, "NDNPY")

SUCCESS_MESSAGE = "Image processed successfully"


# 이미지를 Base64로 인코딩하는 함수
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


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
        if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):  # 이미지 파일 확장자 확인
            img_path = os.path.join(input_directory, img_name)
            features_path = os.path.join(
                output_directory, os.path.splitext(img_name)[0] + '.npy')
            features_dict[img_path] = extract_and_save_features(
                img_path, features_path, model)
    return features_dict


def find_similar_images(target_features, features_dict, top_n=5):
    similarities = {}
    for path, features in features_dict.items():
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):  # 다시 한번 이미지 파일만 처리
            sim = 1 - distance.cosine(target_features, features)
            similarities[path] = sim
    sorted_similarities = sorted(
        similarities.items(), key=lambda x: x[1], reverse=True)
    return sorted_similarities[:top_n]


def return_images(image_bytes, top_n):
    # 모델 로드
    base_model = VGG16(weights='imagenet')
    model = Model(inputs=base_model.input,
                  outputs=base_model.get_layer('fc2').output)

    # 이미지 입력
    # 바이트 데이터로부터 이미지 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file_path = tmp_file.name

    # 입력 이미지의 features 만들기
    temp_features = extract_and_save_features(
        tmp_file_path, tmp_file_path + ".npy", model)  # 임시 파일의 경로를 사용

    # 데이터셋에서 features 딕셔너리 만들기
    features_dict = dataset_features_to_dictionary(
        DATA_ND_DIRECTORY, DATA_NPY_DIRECTORY, model)

    # 유사 이미지 찾기
    similar_images = find_similar_images(temp_features, features_dict, top_n)

    # 임시 파일 삭제
    os.remove(tmp_file_path)

    return similar_images


def test_code():
    # 모델 로드
    base_model = VGG16(weights='imagenet')
    model = Model(inputs=base_model.input,
                  outputs=base_model.get_layer('fc2').output)

    # 입력 이미지
    input_img_path = "E:\\Languages\\Apache24\\ComfyUI_API\\input\\search.pstatic.jpg"
    base_name = os.path.basename(input_img_path)
    if not os.path.exists(INPUT_NPY_DIRECTORY):
        os.makedirs(INPUT_NPY_DIRECTORY)

    # 입력 이미지의 features 만들기
    input_npy_path = os.path.join(
        INPUT_NPY_DIRECTORY, f"{os.path.splitext(base_name)[0]}.npy")
    target_features = extract_and_save_features(
        input_img_path, input_npy_path, model)

    # 데이터셋에서 features 딕셔너리 만들기
    features_dict = dataset_features_to_dictionary(
        DATA_ND_DIRECTORY, DATA_NPY_DIRECTORY, model)

    # 유사 이미지 찾기
    similar_images = find_similar_images(target_features, features_dict)

    for img, sim in similar_images:
        print(f"{img}: 유사도 = {sim}")


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
CORS(app)


@app.route('/get_similar_dresses', methods=['POST'])
def get_similar_dresses():
    try:
        # 요청 본문의 크기를 로그로 출력
        content_length = request.content_length
        print(f"try Request content length: {content_length} bytes")
        print(request.form)
        image_data = request.form['imageData']
        if image_data.startswith('data:image/jpeg;base64,'):
            image_data = image_data.split('data:image/jpeg;base64,')[1]
        else:
            return jsonify({"error": "Invalid image format"}), 400

        # base64 문자열을 이미지로 변환
        image_bytes = base64.b64decode(image_data)

        similar_images = return_images(
            image_bytes, top_n=5)  # 상위 N개 이미지만 반환
        print(similar_images)

        # 유사한 이미지의 경로를 가져와 base64로 인코딩
        if similar_images:
            encoded_images = [encode_image_to_base64(
                img_path) for img_path, _ in similar_images]  # 각 이미지 경로에 대해 base64 인코딩
            return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})
        else:
            return jsonify({"error": "No similar images found"}), 404

    except Exception as e:
        # 요청 본문의 크기를 로그로 출력
        content_length = request.content_length
        print(f"Exception Request content length: {content_length} bytes")
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/")
def main():
    return "Connected"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=1558)
