# from api.open_websocket import open_websocket_connection
# from api.websocket_api import clear_comfy_cache


# _, SERVER_ADDRESS, _ = open_websocket_connection()
# print(clear_comfy_cache(SERVER_ADDRESS, unload_models=True, free_memory=True))

from numba import cuda

device = cuda.get_current_device()
device.reset()
