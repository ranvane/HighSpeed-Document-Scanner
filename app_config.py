import os
import sys
from loguru import logger
import configparser
from pathlib import Path
import platform
from datetime import datetime  # 新增导入，用于获取当前时间


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
                            path = path.replace("$HOME",
                                                os.path.expanduser("~"))
                            return path
            except Exception as e:
                print(f"警告：无法解析 XDG_PICTURES_DIR，使用默认路径。错误: {e}")
        return str(Path.home() / "Pictures")

    elif system == "Darwin":
        # macOS 通常默认图片目录为 ~/Pictures
        return str(Path.home() / "Pictures")

    else:
        # 未知系统，退回到用户目录
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
        'save_location': str(save_folder),  # 添加保存文件夹路径
        'save_naming_format': '%Y%m%d_%H%M%S',  # 新增：默认按当前时间命名
        'temp_location': 'temp'
    },
    'CAMERA': {
        'ip_address': 'http://admin:admin@192.168.10.10:8081/',
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
    # config = configparser.ConfigParser()
    # 禁用默认字符串插值机制
    config = configparser.ConfigParser(interpolation=None)

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


if __name__ == "__main__":
    # 初始化配置
    config = get_config()
    # save_config()
    logger.info(f"当前配置内容: {config._sections}")

    # 获取保存路径
    save_location = config.get('PATHS', 'save_location')
    # 从配置中获取保存文件命名格式
    naming_format = config.get('PATHS', 'save_naming_format')

    logger.info(f"save_location: {save_location}")
    logger.info(f"naming_format: {naming_format}")

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime(naming_format)
    file_name = f"{timestamp}.jpg"

    logger.info(f"file_name: {file_name}")
