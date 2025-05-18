import os
import sys
from loguru import logger 

# 定义环境标志
IS_PRODUCTION = os.path.dirname(os.path.abspath(
    sys.argv[0])) == '/usr/local/bin'
logger.info(f"IS_PRODUCTION: {IS_PRODUCTION}")
# # 定义资源路径
# if IS_PRODUCTION:
#     # 生产环境：使用 /usr/share/wallpaper-changer
#     RESOURCE_PATH = "/usr/share/wallpaper-changer"
#     setup_logging(logging.INFO, IS_PRODUCTION)
# else:
#     # 开发环境：使用当前文件所在目录
#     RESOURCE_PATH = os.path.dirname(os.path.abspath(__file__))
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s | %(levelname)-5s | %(filename)s | %(funcName)s | %(lineno)d | %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )