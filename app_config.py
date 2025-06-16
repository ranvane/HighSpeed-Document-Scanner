import os
import sys
from loguru import logger
import configparser
from pathlib import Path


# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.ini"

# 默认配置项
DEFAULT_CONFIG = {
    'PATHS': {
        'save_location': 'Picture',
        'temp_location': 'temp'
    },
    'CAMERA': {
        'ip_address': 'http://admin:admin@192.168.1.5:8081/',
        'resolution': '1920x1080'
    },
    'SCANNER': {
        'dpi': '300',
        'color_mode': ''
    }
}


def get_config():
    """获取配置，如果不存在则创建默认配置
    返回值:
        ConfigParser对象: 包含所有配置项的对象
    """
    # 创建ConfigParser实例
    config = configparser.ConfigParser()

    # 如果配置文件不存在则创建
    if not CONFIG_FILE.exists():
        # 加载默认配置字典
        config.read_dict(DEFAULT_CONFIG)
        # 写入配置文件
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
        logger.info(f"Created new config file at {CONFIG_FILE}")
    else:
        # 配置文件存在则直接读取
        config.read(CONFIG_FILE)

    # 确保所有配置项都存在，不存在则设为空
    for section, options in DEFAULT_CONFIG.items():
        # 检查配置节是否存在
        if not config.has_section(section):
            config.add_section(section)
        # 检查每个配置项是否存在
        for option in options:
            if not config.has_option(section, option):
                # 设置默认空值
                config.set(section, option, '')

    return config


def save_config(config, section=None, option=None, value=None):
    """保存配置到文件
    参数:
        config: ConfigParser对象
        section: 要更新的节名(可选)
        option: 要更新的选项名(可选)
        value: 要设置的值(可选)
    """
    # 如果提供了section/option/value，则更新配置
    if all([section, option, value is not None]):
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, str(value))
        logger.info(f"Updated config: {section}.{option} = {value}")

    # 保存到文件
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    logger.info(f"Config saved to {CONFIG_FILE}")