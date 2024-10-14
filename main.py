from utils.actions.human_plus_dress import human_plus_dress
from utils.actions.load_workflow import load_workflow
from api.api_helpers import clear
import sys
import os


def main():
    try:
        print("Welcome to the program!")
        workflow = load_workflow('./workflows/workflow_api.json')

        # Positive Prompt 파일 읽기
        with open('./prompt/positive.txt', 'r', encoding='UTF-8') as file:
            positive_prompt = file.read().strip()

        # Negative Prompt 파일 읽기
        with open('./prompt/negative.txt', 'r', encoding='UTF-8') as file:
            negative_prompt = file.read().strip()

        # 입력사진 위치
        image_path = os.path.join(os.getcwd(), 'input', 'test5.jpg')
        print("Image path: " + image_path)

        # 실행
        human_plus_dress(workflow, image_path, positive_prompt,
                         negative_prompt, save_previews=True)
    except Exception as e:
        print(f"main An error occurred: {e}")
        exit_program()


def exit_program():
    print("Exiting the program...")
    sys.exit(0)


def clear_comfy():
    clear(True, True)


main()
