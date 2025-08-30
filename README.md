## Webpage for test
<img src="https://github.com/user-attachments/assets/043635ee-cad9-461c-8f99-a4387bbb3734" alt="Image" width="44%" />
<img src="https://github.com/user-attachments/assets/e54554a5-8b09-49d0-a714-9b279dd4a4e4" alt="Image" width="32%" />
<img src="https://github.com/user-attachments/assets/1879ad0a-6349-4d56-b0b4-5bbe717214ea" alt="Image" width="70%" />

## Used ComfyUI

- ComfyUI Revision: 2652 [0c7c98a9] \*DETACHED | Released on '2024-09-05'

```
Import times for custom nodes:
0.0 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\websocket_image_save.py
0.0 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI-Custom-Scripts
0.0 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI_essentials
0.0 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\rgthree-comfy
0.1 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\comfyui_controlnet_aux
0.1 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\comfyui_segment_anything
0.3 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI_CatVTON_Wrapper
0.3 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI-Manager
0.6 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI-tbox
1.1 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI-Impact-Pack
2.1 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\IDM-VTON
3.6 seconds: E:\ComfyUI_0.2.2\ComfyUI\custom_nodes\ComfyUI_LayerStyle

Starting server
```

## Workflows
- human_plus_dress.json (a person with prompts-> dressed)
![스크린샷 2024-12-27 041251](https://github.com/user-attachments/assets/9f768ae1-884f-4c85-83d4-60d0809a1df1)

- new_dress.json (with promts -> dressed person)
![스크린샷 2024-12-27 041740](https://github.com/user-attachments/assets/68befeeb-943d-4240-83f6-47368b8aa2e0)

- SanAI_CatVTON.json (person + dress image -> dress)
![스크린샷 2024-12-27 043612](https://github.com/user-attachments/assets/d55b0944-639f-41b8-a2c4-d34fa7c9fb65)

- yisol IDM VTON
![스크린샷 2024-12-27 043933](https://github.com/user-attachments/assets/61361e17-4449-4e6c-957d-b5d0318b54f2)

## Reference

#### ComfyUI API


- https://github.com/9elements/comfyui-api

#### IDM-VTON CustomNode

- https://github.com/neuralninja22/IDM-VTON

#### CAT-VTON CustomNode

- https://github.com/Zheng-Chong/CatVTON
- https://github.com/chflame163/ComfyUI_CatVTON_Wrapper

## Current Workflows Setup

### Checkpoint

- [Beautiful Realistic Asians](https://civitai.com/models/25494?modelVersionId=63786)

### VAE

- [vae-ft-mse-840000-ema-pruned](https://huggingface.co/stabilityai/sd-vae-ft-mse-original/blob/main/vae-ft-mse-840000-ema-pruned.ckpt)

## Used FrontEnd
- https://github.com/Roniebin/Armigo_
