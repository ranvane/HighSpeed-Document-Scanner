import os
import platform
import configparser
from pathlib import Path
from datetime import datetime
from loguru import logger


def get_pictures_folder():
    """
    获取系统图片文件夹路径，支持 Windows、Linux 和 macOS 系统。
    Windows: 使用 shell API 获取系统“图片”路径。
    Linux:   解析 ~/.config/user-dirs.dirs 中的 XDG_PICTURES_DIR（若存在）。
    macOS:   返回 ~/Pictures。
    """
    system = platform.system()

    if system == "Windows":
        try:
            from win32com.shell import shell, shellcon
            return shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, None, 0)
        except Exception as e:
            print(f"警告：无法获取 Windows 图片文件夹，使用默认路径。错误: {e}")
            return str(Path.home() / "Pictures")

    elif system == "Linux":
        config_file = os.path.expanduser("~/.config/user-dirs.dirs")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("XDG_PICTURES_DIR"):
                            path = line.split("=")[1].strip().strip('"')
                            path = path.replace("$HOME", os.path.expanduser("~"))
                            return path
            except Exception as e:
                print(f"警告：无法解析 XDG_PICTURES_DIR，使用默认路径。错误: {e}")
        return str(Path.home() / "Pictures")

    elif system == "Darwin":
        return str(Path.home() / "Pictures")

    else:
        return str(Path.home())


# 获取系统图片文件夹路径
pictures_folder = Path(get_pictures_folder())
# 定义保存文件夹路径
save_folder = pictures_folder / "HighSpeed-Document"
# 若保存文件夹不存在则创建
save_folder.mkdir(parents=True, exist_ok=True)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.ini"

# 默认配置项
DEFAULT_CONFIG = {
    'PATHS': {
        'save_location': str(save_folder),
        'save_naming_format': '%Y%m%d_%H%M%S',
        'temp_location': 'temp'
    },
    'CAMERA': {
        'ip_address': 'http://admin:admin@192.168.10.10:8081/',  # 网络摄像头地址
        'resolution': '1920x1080',
        'use_usb_camera': 1,  # 是否使用 USB 摄像头，False 表示默认使用本地摄像头
        'usb_index': 0  # USB 摄像头索引，默认使用 0 号摄像头
    },
    'SCANNER': {
        'dpi': '300',
        'color_mode': 'rgb'
    }
}

# 参数中文名映射
PARAM_LABELS = {
    'save_location': '保存路径',
    'save_naming_format': '命名格式',
    'temp_location': '临时目录',
    'ip_address': '摄像头地址',
    'resolution': '分辨率',
    'dpi': '扫描精度',
    'color_mode': '颜色模式',
}


def reset_config_to_default():
    """
    重置配置为默认配置并保存到 config.ini，同时写入参数中文名映射
    """
    config = configparser.ConfigParser(interpolation=None)
    config.read_dict(DEFAULT_CONFIG)

    config.add_section('LABELS')
    for key, label in PARAM_LABELS.items():
        config.set('LABELS', key, label)

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

    logger.info("配置文件已重置为默认设置，包含参数中文名映射。")


def get_config():
    """
    获取配置，如果不存在则创建默认配置
    返回:
        configparser.ConfigParser 对象
    """
    config = configparser.ConfigParser(interpolation=None)

    if not CONFIG_FILE.exists():
        reset_config_to_default()
    else:
        config.read(CONFIG_FILE, encoding='utf-8')

    # 确保所有配置项都存在，不存在则设为空字符串
    for section, options in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            config.add_section(section)
        for option in options:
            if not config.has_option(section, option):
                config.set(section, option, '')

    # 确保 LABELS 节存在
    if not config.has_section('LABELS'):
        config.add_section('LABELS')
        for key, label in PARAM_LABELS.items():
            config.set('LABELS', key, label)

    return config


def get_labels_from_config(config):
    """
    从配置文件读取参数中文名映射，返回字典
    """
    if config.has_section('LABELS'):
        return dict(config.items('LABELS'))
    return {}


def save_config(config, section=None, option=None, value=None):
    """
    保存配置到文件
    """
    if all([section, option, value is not None]):
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, str(value))
        logger.info(f"Updated config: {section}.{option} = {value}")

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

    logger.info(f"Config saved to {CONFIG_FILE}")


if __name__ == "__main__":
    # 重置配置为默认值（含中文映射）
    reset_config_to_default()

    config = get_config()
    labels = get_labels_from_config(config)

    logger.info(f"当前配置内容: {config._sections}")
    logger.info(f"参数中文映射: {labels}")

    # 测试时间命名格式
    naming_format = config.get('PATHS', 'save_naming_format')
    timestamp = datetime.now().strftime(naming_format)
    file_name = f"{timestamp}.jpg"
    logger.info(f"生成的文件名示例: {file_name}")
