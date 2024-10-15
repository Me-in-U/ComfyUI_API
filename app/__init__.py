from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from api.open_websocket import open_websocket_connection
from api.websocket_api import clear_comfy_cache
from utils.actions.human_plus_dress import human_plus_dress
from utils.actions.new_dress import new_dress
from utils.actions.load_workflow import load_workflow
from flask_cors import CORS  # CORS 모듈 추가
import os
import base64
import traceback

app = Flask(__name__)


# CORS(app, resources={r"/*": {"origins": "http://real.pinkbean.co.kr:1557"}})
CORS(app)


@app.route('/')
def main():
    return render_template("index.html")


# 이미지를 Base64로 인코딩하는 함수
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        return jsonify({"message": "POST request received"}), 200
    else:  # GET 요청 처리
        return jsonify({"message": "GET request received"}), 200


@app.route('/human_plus_dress', methods=['POST'])
def img_human_plus_dress():
    try:
        workflow = load_workflow(
            "E:\Languages\Apache24\ComfyUI_API\workflows\human_plus_dress_api.json")

        # 사진 읽고 저장
        image_file = request.files['image1']
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(
            "E:\Languages\Apache24\ComfyUI_API\input", filename)
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

        return jsonify({"message": "Image processed successfully", "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/new_dress', methods=['POST'])
def img_new_dress():
    try:
        workflow = load_workflow(
            "E:\Languages\Apache24\ComfyUI_API\workflows\\new_dress_api.json")
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

        return jsonify({"message": "Image processed successfully", "results": encoded_images})

    except Exception as e:
        print("Error:", e)
        print("Form data received:", request.form)
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e), "form_data": request.form.to_dict()}), 500


@app.route('/vton_dress', methods=['POST'])
def img_vton_dress():
    try:
        workflow = load_workflow(
            "E:\Languages\Apache24\ComfyUI_API\workflows\\vton_dress.json")

        # 사진 읽고 저장
        image_file1 = request.files['image1']
        filename1 = secure_filename(image_file1.filename)
        image_path1 = os.path.join(
            "E:\Languages\Apache24\ComfyUI_API\input", filename1)
        image_file1.save(image_path1)

        # 사진 읽고 저장
        image_file2 = request.files['image2']
        filename2 = secure_filename(image_file2.filename)
        image_path2 = os.path.join(
            "E:\Languages\Apache24\ComfyUI_API\input", filename2)
        image_file2.save(image_path2)

        # 실행 및 결과 이미지 경로 받기
        result_image_paths = human_plus_dress(
            workflow, image_path1, image_path2, save_previews=True)

        # 메모리 비우기
        _, server_address, _ = open_websocket_connection()
        clear_comfy_cache(server_address=server_address,
                          unload_models=True, free_memory=True)

        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        return jsonify({"message": "Image processed successfully", "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
