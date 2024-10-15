import json
from PIL import Image
import io
import os

# Assuming the import paths are correct and the methods are defined elsewhere:
from api.websocket_api import queue_prompt, get_history, get_image, upload_image, clear_comfy_cache
from api.open_websocket import open_websocket_connection


def generate_image_by_prompt(prompt, output_path, save_previews=False):
    try:
        ws, server_address, client_id = open_websocket_connection()
        prompt_id = queue_prompt(prompt, client_id, server_address)[
            'prompt_id']
        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address, save_previews)
        save_image(images, output_path, save_previews)
    finally:
        ws.close()


def generate_image_by_prompt_and_image(prompt, output_path, input_path, filename, save_previews=False):
    try:
        print("generate_image_by_prompt_and_image")
        ws, server_address, client_id = open_websocket_connection()
        print(ws, server_address, client_id)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Uploading image~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        upload_image(input_path, filename, server_address)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~done~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        prompt_id = queue_prompt(prompt, client_id, server_address)[
            'prompt_id']
        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address, save_previews)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Saving image~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        save_image(images, output_path, save_previews)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~done~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    finally:
        ws.close()


def generate_image_by_prompt(prompt, output_path, save_previews=False):
    try:
        print("generate_image_by_prompt_and_image")
        ws, server_address, client_id = open_websocket_connection()
        print(ws, server_address, client_id)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~done~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        prompt_id = queue_prompt(prompt, client_id, server_address)[
            'prompt_id']
        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address, save_previews)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Saving image~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        save_image(images, output_path, save_previews)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~done~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    finally:
        ws.close()


def save_image(images, output_path, save_previews):
    try:
        # 파일을 쓰기 모드로 열면 기존 내용이 삭제됩니다.
        with open('tempImage.txt', 'w') as file:
            pass  # 파일을 열고 아무 작업도 하지 않으면 내용이 초기화됩니다.
        print("tempImage.txt has been cleared.")
    except Exception as e:
        print(f"Failed to clear tempImage.txt: {e}")

    # tempImage.txt 파일을 업데이트 모드로 열기
    with open('tempImage.txt', 'a') as log_file:
        for itm in images:
            print(itm)
            # 이미지 데이터가 있는지 확인
            if 'image_data' not in itm:
                print(
                    f"Failed to save image {itm['file_name']}: 'image_data' key not found")
                continue  # 데이터가 없으면 다음 이미지로 넘어감

            # 저장할 디렉터리 설정
            directory = os.path.join(
                output_path, 'temp/') if itm['type'] == 'temp' and save_previews else output_path
            os.makedirs(directory, exist_ok=True)

            try:
                # 이미지 저장
                image = Image.open(io.BytesIO(itm['image_data']))
                image_path = os.path.join(directory, itm['file_name'])
                image.save(image_path)
                print(
                    f"Successfully saved image {itm['file_name']} in {directory}")

                # 로그 파일에 이미지 경로 기록
                log_file.write(image_path + '\n')

            except IOError as io_err:
                # 저장 오류에 대한 구체적인 예외 처리
                print(
                    f"IOError - failed to save image {itm['file_name']}: {io_err}")
            except Exception as e:
                # 이미지가 저장된 후 발생한 예외는 무시하고 로그로만 출력
                print(f"Image saved but encountered an error afterwards: {e}")
            print()


def track_progress(prompt, ws, prompt_id):
    node_ids = list(prompt.keys())
    finished_nodes = []

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'progress':
                data = message['data']
                current_step = data['value']
                print('In K-Sampler -> Step: ',
                      current_step, ' of: ', data['max'])
            if message['type'] == 'execution_cached':
                data = message['data']
                for itm in data['nodes']:
                    if itm not in finished_nodes:
                        finished_nodes.append(itm)
                        print('Progress: ', len(finished_nodes),
                              '/', len(node_ids), ' Tasks done')
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] not in finished_nodes:
                    finished_nodes.append(data['node'])
                    print('Progress: ', len(finished_nodes),
                          '/', len(node_ids), ' Tasks done')

                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data
    return


def get_images(prompt_id, server_address, allow_preview=False):
    output_images = []

    history = get_history(prompt_id, server_address)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                output_data = {}
                if allow_preview and image['type'] == 'temp':
                    preview_data = get_image(
                        image['filename'], image['subfolder'], image['type'], server_address)
                    output_data['image_data'] = preview_data
                if image['type'] == 'output':
                    image_data = get_image(
                        image['filename'], image['subfolder'], image['type'], server_address)
                    output_data['image_data'] = image_data
                output_data['file_name'] = image['filename']
                output_data['type'] = image['type']
                output_images.append(output_data)

    return output_images


def clear():
    clear_comfy_cache()
