from itertools import chain
import json
import shutil
import time
import os
import base64
import sys
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, redirect, request, jsonify, render_template
from api.websocket_api import clear_comfy_cache, get_queue_size
from api.open_websocket import open_websocket_connection
from similarity.getSimilarity import return_images, return_images2
from utils.actions.new_dress import new_dress
from utils.actions.vton_dress import vton_dress
from utils.actions.load_workflow import load_workflow
from utils.actions.human_plus_dress import human_plus_dress
import psutil
from PIL import Image

BASE_DIRECTORY = "E:\\Languages\\Apache24\\ComfyUI_API"
COMFYUI_INPUT_DIR = "E:\\ComfyUI_0.2.2\\ComfyUI\\input"
COMFYUI_OUTPUT_DIR = "E:\\ComfyUI_0.2.2\\ComfyUI\\output"
INPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "input")
OUTPUT_DIRECTORY = os.path.join(BASE_DIRECTORY, "output")
WORKFLOW_DIRECTORY = os.path.join(BASE_DIRECTORY, "workflows")
SUCCESS_MESSAGE = "Image processed successfully"
SUCCESS_MESSAGE_TEST = "TEST Completed successfully"
SERVER_ADDRESS = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
CORS(app)

IMAGECOUNT = 0
IMAGEPATHMAPPING = {}


# CORS(app, resources={r"/*": {"origins": "http://real.pinkbean.co.kr:1557"}})


#! 테스트 코드------------------------------------------------
# @app.route('/test')
# def get_path():
#     return str(sys.path)

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
            if 'python_embeded' in cmdline:
                print("cmdline => ", cmdline)
                print("ComfyUI 실행중")
                return True
    print("ComfyUI 꺼져있음")
    return False


def run_comfyui():
    os.system(
        r'start "" "E:\\ComfyUI_0.2.2\\python_embeded\\python.exe" -s "E:\\ComfyUI_0.2.2\\ComfyUI\\main.py" --windows-standalone-build')


def terminate_comfyui():
    # cmdline에 'ComfyUI'라는 단어가 포함된 프로세스를 찾아 종료
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'python.exe':
            cmdline = ' '.join(process.info['cmdline'])
            if 'python_embeded' in cmdline:
                process.terminate()  # 프로세스 종료
                process.wait()       # 프로세스 종료 대기
                print("ComfyUI 종료됨")
                global SERVER_ADDRESS
                SERVER_ADDRESS = None


def clear_memory():
    _, server_address, _ = open_websocket_connection()
    clear_comfy_cache(server_address=server_address,
                      unload_models=True, free_memory=True)


@app.route('/')
def main():
    global SERVER_ADDRESS
    # comfyUI 켜야함
    if not is_comfyui_running():
        print("Execute ComfyUI")
        # 프로세스가 없으면 comfyUI 실행
        run_comfyui()
        # 일단 loading.html 반환
        print("로딩화면 전송")
        return render_template("loading.html")

    # comfyUI 서버가 실행 중이라면 바로 index.html 반환
    try:
        _, SERVER_ADDRESS, _ = open_websocket_connection()
        print("SERVER_ADDRESS : ", SERVER_ADDRESS)
        return render_template("index.html")
    except:
        SERVER_ADDRESS = None
        print("로딩화면 전송")
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
        print(request.form)
        print(request.files)
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

        print(image_path)
        # 실행 및 결과 이미지 경로 받기
        result_image_paths = [
            human_plus_dress(
                workflow, image_path, positive_prompt, negative_prompt, save_previews=True)
        ]
        print("result_image_paths :", result_image_paths)

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


@app.route('/new_dress_test', methods=['POST'])
def img_new_dress_test():
    try:
        result_image_paths = [
            ".\\output\\T1.png",
            ".\\output\\T2.png",
            ".\\output\\T3.png"
        ]
        print("result_image_paths :", result_image_paths)

        image_map_keys = []
        global IMAGEPATHMAPPING
        global IMAGECOUNT
        #  new_dress 이미지 경로를 imagePathMapping에 추가
        for path in result_image_paths:
            IMAGEPATHMAPPING[IMAGECOUNT] = path
            image_map_keys.append(IMAGECOUNT)
            IMAGECOUNT += 1  # imagecount를 증가시켜 다음 키로 설정

        # 비슷한 이미지 찾기
        similar_images = [
            [('E:\\Languages\\Apache24\\ComfyUI_API\\output\\ND\\dress_1214.jpg',
              0.6821891174346819)],
            [('E:\\Languages\\Apache24\\ComfyUI_API\\output\\ND\\dress_621.jpg',
              0.7606961665896327)],
            [('E:\\Languages\\Apache24\\ComfyUI_API\\output\\ND\\dress_542.jpg',
              0.7869456237193144)]
        ]  # 상위 N개 이미지만 반환
        print(similar_images)

        #  similar_images 경로를 imagePathMapping에 추가
        for image in similar_images:
            path = image[0][0]
            result_image_paths.append(path)
            IMAGEPATHMAPPING[IMAGECOUNT] = path
            image_map_keys.append(IMAGECOUNT)
            IMAGECOUNT += 1  # imagecount를 증가시켜 다음 키로 설정
        print(image_map_keys)

        print(IMAGEPATHMAPPING)
        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        return jsonify({"message": SUCCESS_MESSAGE_TEST, "results": encoded_images, "imageMapKeys": image_map_keys}, )

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/new_dress', methods=['POST'])
def img_new_dress():
    try:
        # 워크플로우 로드
        workflow_path = os.path.join(WORKFLOW_DIRECTORY, "new_dress_api.json")
        workflow = load_workflow(workflow_path)

        # Check for a direct positive_prompt from the form
        positive_prompt = request.form.get('positive_prompt', None)
        if not positive_prompt:
            # 사용자 프롬프트 읽기
            options_str = request.form.get('options', '[]')

            # null (Python의 None) 값을 제거
            options_list = json.loads(options_str)  # JSON 문자열을 리스트로 변환
            options_list = [opt for opt in options_list if opt is not None]
            positive_prompt = ', '.join(options_list)  # 리스트의 단어들을 쉼표로 구분하여 추가

            # 'otherInput' 값이 '[]'이면 빈 문자열로 처리
            other_input = request.form.get('otherInput', '')
            if other_input == '[]':
                other_input = ''  # 빈 리스트처럼 들어오면 빈 문자열로 처리
            else:
                positive_prompt += other_input

            # positive_prompt에 otherInput 추가
            positive_prompt += '(white dress:1.2), (luxury wedding dress:1.3), bride,long dress,elegant floor-length skirt,(korean1.2), Best Quality, (Masterpiece:1.4), (Realism:1.2), (Realisitc:1.2), 4K,(photorealistic:1.3), Detailed, 1 girl, beautiful and pretty girl, (black background: 1.3), photo-realistic, realism, finely detail, Super Resolution, super detail, ultra-detailed, ultra high res, RAW photo, detailed cafe, perfect fingers, beautiful face, beautiful detailed eyes, symmetric eyes'

        negative_prompt = request.form.get('negative_prompt', "(black color dress:1.5),black color accessories,Paintings,sketches, (worst quality, low quality, normal quality:1.7),lowres, blurry, text, logo, ((monochrome)), ((grayscale)), easynegative, badhandv, , wrong finger, lowres, bad anatomy, bad handsmissing fingers,extra digit ,fewer digits,signature,watermark, username, blurry, bad feet, fused girls, fushion, signature, watermark, username, blurry, (bad feet:1.1),, monochrome, duplicate, morbid, mutilated, long neck, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, bad proportions, malformed limbs, extra limbs, cloned face, disfigured, gross proportions, (missing arms:1.331), (missing legs:1.331), (extra arms:1.331), (extra legs:1.331), plump, bad legs, bad anatomy, bad hands, text, error, missing fingers,watermark, username, blurry, long body, bad anatomy, bad hands, missing fingers, pubic hair,extra digit, fewer digits, bad anatomy, bad hands, missing fingers, signature, watermark, username, blurry,huge breasts,Large Breasts,kid,children,extra hands,extra arms,((disfigured)), ((bad art)), ((deformed)),ugly face,umbrella,deformed face,malformed face,extra head, easynegative, badhandv4,Big Breasts,multiple girls, multiple view,Big Breasts,multiple girls, multiple views,Long Necks,Long Torso,  bad_pictures")

        # 실행 및 결과 이미지 경로 받기
        result_image_paths = []
        for i in range(0, 6, 2):
            relative_path = new_dress(
                workflow, positive_prompt, negative_prompt, save_previews=True)
            absolute_path = os.path.join(
                COMFYUI_OUTPUT_DIR, os.path.relpath(relative_path, './output'))
            result_image_paths.append(absolute_path)
            result_image_paths.append(return_images2(
                result_image_paths[i], top_n=1)[0][0])

        image_map_keys = []
        encoded_images = []
        global IMAGEPATHMAPPING
        global IMAGECOUNT
        #  이미지 경로를 imagePathMapping에 추가
        for path in result_image_paths:
            IMAGEPATHMAPPING[IMAGECOUNT] = path
            image_map_keys.append(IMAGECOUNT)
            IMAGECOUNT += 1  # imagecount를 증가시켜 다음 키로 설정
            # 결과 이미지를 Base64로 인코딩하여 반환
            encoded_images.append(encode_image_to_base64(path))
        print(IMAGEPATHMAPPING)

        # 메모리 비우기
        clear_memory()

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images, "imageMapKeys": image_map_keys}, )

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@ app.route('/vton_dress', methods=['POST'])
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
        result_image_paths = [
            vton_dress(
                workflow, image_path1, image_path2, save_previews=True)
        ]

        # 메모리 비우기
        clear_memory()

        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@ app.route('/vton_dress_multi_test', methods=['POST'])
def img_vton_dress_multi_test():
    try:
        print(request.form)
        print(request.files)

        # 드레스
        dress_file_index_array = request.form['ImageFileIndexArray']
        print(dress_file_index_array)

        # 쉼표로 구분된 문자열을 정수 리스트로 변환
        dress_file_index_list = [int(index.strip())
                                 for index in dress_file_index_array.split(',')]
        print("dress_file_index_list:", dress_file_index_list)

        # IMAGEPATHMAPPING에서 키값으로 값을 찾아 리스트 생성
        dress_image_paths = [IMAGEPATHMAPPING[index]
                             for index in dress_file_index_list if index in IMAGEPATHMAPPING]
        print("dress_image_paths:", dress_image_paths)

        # 사진 읽고 저장
        image_file = request.files['myPic']
        print("image_file", image_file)
        filename = image_file.filename
        human_image_path = os.path.join(INPUT_DIRECTORY, filename)
        print("image_path", human_image_path)
        image_file.save(human_image_path)

        # 실행 및 결과 이미지 경로 받기
        result_image_paths = []
        for dress_image_path in dress_image_paths:
            output_path = os.path.join(
                "E:\\Languages\\Apache24\\ComfyUI_API\\TEST_IMAGE", f"merged_{os.path.basename(dress_image_path)}")
            # vton_dress를 각 드레스 이미지 경로에 대해 실행
            print("드레스 :", dress_image_path)
            print("사람 :", human_image_path)
            background = Image.open(dress_image_path)
            foreground = Image.open(
                "E:\\Languages\\Apache24\\ComfyUI_API\\TEST_IMAGE\\TEST_IMG.png")
            (img_h, img_w) = background.size
            resize_back = foreground.resize((img_h, img_w))
            resize_back.paste(foreground, (0, 0), foreground)

            # 결과 이미지를 저장
            background.save(output_path)
            result_image_paths.append(output_path)  # 저장된 파일 경로 추가

            print("결과 이미지 저장 경로:", output_path)
        print(result_image_paths)

        # 결과 이미지를 Base64로 인코딩하여 반환
        encoded_images = [encode_image_to_base64(
            path) for path in result_image_paths]

        encoded_images.append(encode_image_to_base64(human_image_path))

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@ app.route('/vton_dress_multi', methods=['POST'])
def img_vton_dress_multi():
    try:
        # 워크플로우 로드
        workflow_path = os.path.join(WORKFLOW_DIRECTORY, "vton_api.json")
        workflow = load_workflow(workflow_path)

        # 드레스
        dress_file_index_array = request.form['ImageFileIndexArray']

        # 쉼표로 구분된 문자열을 정수 리스트로 변환
        selected_dress_index = [int(index.strip())
                                for index in dress_file_index_array.split(',')]

        # IMAGEPATHMAPPING에서 키값으로 값을 찾아 리스트 생성
        dress_image_paths = [IMAGEPATHMAPPING[index]
                             for index in selected_dress_index if index in IMAGEPATHMAPPING]

        # # 사진 읽고 저장
        image_file = request.files['myPic']
        filename = image_file.filename
        human_image_path = os.path.join(INPUT_DIRECTORY, filename)
        image_file.save(human_image_path)

        # 실행 및 결과 이미지 경로 받기
        encoded_images = []
        for dress_image_path in dress_image_paths:
            # vton_dress를 각 드레스 이미지 경로에 대해 실행
            vton_image_path = vton_dress(
                workflow, human_image_path, dress_image_path, save_previews=True)
            # 결과 이미지를 Base64로 인코딩하여 반환
            encoded_images.append(encode_image_to_base64(vton_image_path))

        # 누군가를 위한 사람이미지 추가
        encoded_images.append(encode_image_to_base64(human_image_path))

        # 메모리 비우기
        clear_memory()

        return jsonify({"message": SUCCESS_MESSAGE, "results": encoded_images})

    except Exception as e:
        print(f"Flask An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@ app.route('/get_similar_dresses', methods=['POST'])
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


@ app.route("/queue_size", methods=["GET"])
def queue_size():
    qs = get_queue_size(SERVER_ADDRESS)
    if qs != None:
        return get_queue_size(SERVER_ADDRESS)
    else:
        return jsonify({"error": "Server address is not set"}), 500


if __name__ == "__main__":
    if is_comfyui_running():
        _, SERVER_ADDRESS, _ = open_websocket_connection()
    else:
        run_comfyui()
    print("SERVER_ADDRESS : ", SERVER_ADDRESS)
    app.run(host="0.0.0.0", debug=True, port=1557, threaded=True)
