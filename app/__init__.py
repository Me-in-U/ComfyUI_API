import os
import base64
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template
from api.websocket_api import clear_comfy_cache
from api.open_websocket import open_websocket_connection
from utils.actions.new_dress import new_dress
from utils.actions.vton_dress import vton_dress
from utils.actions.load_workflow import load_workflow
from utils.actions.human_plus_dress import human_plus_dress

app = Flask(__name__)


# CORS(app, resources={r"/*": {"origins": "http://real.pinkbean.co.kr:1557"}})
CORS(app)

BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API"
INPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "input")
OUTPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "output")
WORKFLOW_DIRECTORY = os.path.join(BASE_DIRECTORY, "workflows")
SUCCESS_MESSAGE = "Image processed successfully"


@app.route('/')
def main():
    _, server_address, _ = open_websocket_connection()
    clear_comfy_cache(server_address=server_address,
                      unload_models=True, free_memory=True)
    return render_template("index.html")


# 이미지를 Base64로 인코딩하는 함수
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@app.route('/human_plus_dress', methods=['POST'])
def img_human_plus_dress():
    try:
        # 워크플로우 로드
        workflow_path = os.path.join(
            WORKFLOW_DIRECTORY, "human_plus_dress_api.json")
        workflow = load_workflow(workflow_path)

        # 사진 읽고 저장
        image_file = request.files['image1']
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(INPUT_DIRECTORY, filename)
        image_file.save(image_path)

        # Prompt 파일 읽기
        positive_prompt = request.form['positive_prompt']
        negative_prompt = request.form['negative_prompt']

        # 실행 및 결과 이미지 경로 받기
        result_image_paths = human_plus_dress(
            workflow, image_path, positive_prompt, negative_prompt, save_previews=True)

        # 메모리 비우기
        _, server_address, _ = open_websocket_connection()
        clear_comfy_cache(server_address=server_address,
                          unload_models=True, free_memory=True)

        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/new_dress', methods=['POST'])
def img_new_dress():
    try:
        # 워크플로우 로드
        workflow_path = os.path.join(WORKFLOW_DIRECTORY, "new_dress_api.json")
        workflow = load_workflow(workflow_path)

        # Prompt 파일 읽기
        positive_prompt = request.form['positive_prompt']
        negative_prompt = request.form['negative_prompt']

        # 실행 및 결과 이미지 경로 받기
        result_image_paths = new_dress(
            workflow, positive_prompt, negative_prompt, save_previews=True)

        # 메모리 비우기
        _, server_address, _ = open_websocket_connection()
        clear_comfy_cache(server_address=server_address,
                          unload_models=True, free_memory=True)

        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/vton_dress', methods=['POST'])
def img_vton_dress():
    try:
        # 워크플로우 로드
        workflow_path = os.path.join(WORKFLOW_DIRECTORY, "vton_api.json")
        workflow = load_workflow(workflow_path)

        # 사진 읽고 저장
        image_file1 = request.files['image1']
        filename1 = secure_filename(image_file1.filename)
        image_path1 = os.path.join(INPUT_DIRECTORY, filename1)
        image_file1.save(image_path1)

        # 사진 읽고 저장
        image_file2 = request.files['image2']
        filename2 = secure_filename(image_file2.filename)
        image_path2 = os.path.join(INPUT_DIRECTORY, filename2)
        image_file2.save(image_path2)

        # 실행 및 결과 이미지 경로 받기
        result_image_paths = vton_dress(
            workflow, image_path1, image_path2, save_previews=True)

        # 메모리 비우기
        _, server_address, _ = open_websocket_connection()
        clear_comfy_cache(server_address=server_address,
                          unload_models=True, free_memory=True)

        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
