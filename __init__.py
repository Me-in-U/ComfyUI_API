import time
import os
import base64
import sys
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, redirect, request, jsonify, render_template
from api.websocket_api import clear_comfy_cache, get_queue_size
from api.open_websocket import open_websocket_connection
from similarity.getSimilarity import return_images
from utils.actions.new_dress import new_dress
from utils.actions.vton_dress import vton_dress
from utils.actions.load_workflow import load_workflow
from utils.actions.human_plus_dress import human_plus_dress
import psutil

BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API"
INPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "input")
OUTPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "output")
WORKFLOW_DIRECTORY = os.path.join(BASE_DIRECTORY, "workflows")
SUCCESS_MESSAGE = "Image processed successfully"

SERVER_ADDRESS = None

app = Flask(__name__)
CORS(app)

# CORS(app, resources={r"/*": {"origins": "http://real.pinkbean.co.kr:1557"}})


#! 테스트 코드------------------------------------------------
@app.route('/test')
def get_path():
    return str(sys.path)

# @app.before_request
# def before_request():
#     if request.url.startswith('http://'):
#         url = request.url.replace('http://', 'https://', 1)
#         code = 301
#         return redirect(url, code=code)


@app.route('/1557')
def gg():
    return render_template("faker.html")

#! 테스트 코드------------------------------------------------


#! 이미지 -> Base64로 인코딩
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_comfyui_running():
    # cmdline에 'ComfyUI'라는 단어가 포함된 프로세스가 실행 중인지 확인
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'python.exe':
            cmdline = ' '.join(process.info['cmdline'])
            print(cmdline)
            if 'python_embeded' in cmdline:
                return True
    return False


def terminate_comfyui():
    # cmdline에 'ComfyUI'라는 단어가 포함된 프로세스를 찾아 종료
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'python.exe':
            cmdline = ' '.join(process.info['cmdline'])
            if 'python_embeded' in cmdline:
                process.terminate()  # 프로세스 종료
                process.wait()       # 프로세스 종료 대기
                global SERVER_ADDRESS
                SERVER_ADDRESS = None


@app.route('/')
def main():
    # comfyUI 켜야함
    if not is_comfyui_running():
        # 프로세스가 없으면 comfyUI 실행
        os.system(
            r'start "" "E:\\ComfyUI\\python_embeded\\python.exe" -s "E:\\ComfyUI\\ComfyUI\\main.py" --windows-standalone-build')

        # 일단 loading.html 반환
        return render_template("loading.html")

    # comfyUI 서버가 실행 중이라면 바로 index.html 반환
    try:
        global SERVER_ADDRESS
        _, SERVER_ADDRESS, _ = open_websocket_connection()
        print(SERVER_ADDRESS)
        return render_template("index.html")
    except:
        return render_template("loading.html")


@app.route('/terminate')
def terminate():
    if is_comfyui_running():
        terminate_comfyui()
        return "ComfyUI 프로세스를 종료했습니다."
    else:
        return "ComfyUI 프로세스가 실행 중이 아닙니다."


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


@app.route("/queue_size", methods=["GET"])
def queue_size():
    global SERVER_ADDRESS
    if SERVER_ADDRESS != None:
        return get_queue_size(SERVER_ADDRESS)
    else:
        if not is_comfyui_running():
            SERVER_ADDRESS = None
        else:
            _, SERVER_ADDRESS, _ = open_websocket_connection()
            print("Connected to websocket")
        return jsonify({"error": "Server address is not set"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=1557, threaded=True)
