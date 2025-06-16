import os
import sys
from loguru import logger 

# 定义环境标志
IS_PRODUCTION = os.path.dirname(os.path.abspath(
    sys.argv[0])) == '/usr/local/bin'
logger.info(f"IS_PRODUCTION: {IS_PRODUCTION}")

