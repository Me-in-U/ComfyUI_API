import sys
import logging
import site


site.addsitedir('E:\Languages\Python310\Lib\site-packages')

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, "E:\\Languages\\Apache24\\ComfyUI_API")

from app import app as application