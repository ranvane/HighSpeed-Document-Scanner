# 导入操作系统相关功能模块
import os
# 导入获取系统信息模块
import platform
# 导入配置文件解析模块
import configparser
# 导入路径操作模块
from pathlib import Path
# 导入日期时间处理模块
from datetime import datetime
# 导入日志记录模块
from loguru import logger


def get_pictures_folder():
    """
    获取系统图片文件夹路径，支持 Windows、Linux 和 macOS 系统。
    Windows: 使用 shell API 获取系统“图片”路径。
    Linux:   解析 ~/.config/user-dirs.dirs 中的 XDG_PICTURES_DIR（若存在）。
    macOS:   返回 ~/Pictures。

    Returns:
        str: 系统图片文件夹的路径，如果获取失败则返回默认路径。
    """
    # 获取当前操作系统类型
    system = platform.system()

    if system == "Windows":
        try:
            # 导入 Windows 系统的 shell 相关模块
            from win32com.shell import shell, shellcon
            # 使用 Windows shell API 获取系统“图片”文件夹路径
            return shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, None, 0)
        except Exception as e:
            # 记录警告日志，提示无法获取系统图片路径
            logger.warning(f"无法获取系统图片路径，使用默认路径。错误: {e}")
            # 返回默认图片文件夹路径
            return str(Path.home() / "Pictures")

    elif system == "Linux":
        # 获取 Linux 系统用户目录配置文件路径
        config_file = os.path.expanduser("~/.config/user-dirs.dirs")
        if os.path.exists(config_file):
            try:
                # 打开用户目录配置文件
                with open(config_file, "r", encoding="utf-8") as f:
                    # 逐行读取配置文件
                    for line in f:
                        # 查找包含 XDG_PICTURES_DIR 的行
                        if line.startswith("XDG_PICTURES_DIR"):
                            # 提取图片文件夹路径
                            path = line.split("=")[1].strip().strip('"')
                            # 将 $HOME 替换为实际的用户主目录路径
                            path = path.replace("$HOME", os.path.expanduser("~"))
                            return path
            except Exception as e:
                # 打印警告信息，提示无法解析 XDG_PICTURES_DIR
                print(f"警告：无法解析 XDG_PICTURES_DIR，使用默认路径。错误: {e}")
        # 返回默认图片文件夹路径
        return str(Path.home() / "Pictures")

    elif system == "Darwin":
        # 返回 macOS 系统的默认图片文件夹路径
        return str(Path.home() / "Pictures")

    else:
        # 对于其他操作系统，返回用户主目录路径
        return str(Path.home())


# 获取系统图片文件夹路径，并转换为 Path 对象
pictures_folder = Path(get_pictures_folder())
# 定义保存文件夹路径，在系统图片文件夹下创建 HighSpeed-Document 文件夹
save_folder = pictures_folder / "HighSpeed-Document"
# 若保存文件夹不存在则创建，同时创建其父目录
save_folder.mkdir(parents=True, exist_ok=True)

# 配置文件路径，位于当前文件所在目录下的 config.ini
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
        'color_mode': 'rgb',
        'merge_image_interval': '5',  # 合并图片间隔（单位：px）
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
    'merge_image_interval': '合并图片间隔距离（单位：px）',
}


def reset_config_to_default():
    """
    重置配置为默认配置并保存到 config.ini，同时写入参数中文名映射
    """
    # 创建 ConfigParser 对象，禁用插值功能
    config = configparser.ConfigParser(interpolation=None)
    # 将默认配置读取到 ConfigParser 对象中
    config.read_dict(DEFAULT_CONFIG)

    # 添加 LABELS 配置节
    config.add_section('LABELS')
    # 将参数中文名映射写入 LABELS 配置节
    for key, label in PARAM_LABELS.items():
        config.set('LABELS', key, label)

    # 以写入模式打开配置文件
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        # 将配置写入文件
        config.write(f)

    # 记录信息日志，提示配置文件已重置为默认设置
    logger.info("配置文件已重置为默认设置，包含参数中文名映射。")


def get_config():
    """
    获取配置，如果不存在则创建默认配置
    返回:
        configparser.ConfigParser 对象
    """
    # 创建 ConfigParser 对象，禁用插值功能
    config = configparser.ConfigParser(interpolation=None)

    # 检查配置文件是否存在
    if not CONFIG_FILE.exists():
        # 若不存在则重置为默认配置
        reset_config_to_default()
    else:
        # 若存在则读取配置文件
        config.read(CONFIG_FILE, encoding='utf-8')

    # 补全缺失的 section 和 option（按需补全）
    for section, options in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            # 若配置文件中不存在该 section，则添加
            config.add_section(section)
        for option, default_value in options.items():
            if not config.has_option(section, option):
                # 若配置文件中不存在该 option，则设置默认值
                config.set(section, option, str(default_value))

    # 确保 LABELS 节存在
    if not config.has_section('LABELS'):
        # 若不存在则添加 LABELS 节
        config.add_section('LABELS')
        for key, label in PARAM_LABELS.items():
            # 将参数中文名映射写入 LABELS 节
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
    保存配置到文件。若提供了 section、option 和 value，则更新对应配置项。

    Args:
        config (configparser.ConfigParser): 配置解析器对象，包含当前配置信息。
        section (str, optional): 配置文件中的节名称，默认为 None。
        option (str, optional): 配置文件中节下的选项名称，默认为 None。
        value (any, optional): 要设置给选项的值，默认为 None。
    """
    # 检查 section、option 和 value 是否都不为 None
    if all([section, option, value is not None]):
        # 若配置文件中不存在指定的 section，则添加该 section
        if not config.has_section(section):
            config.add_section(section)
        # 设置指定 section 下 option 的值，将值转换为字符串类型
        config.set(section, option, str(value))
        # 记录信息日志，提示配置项已更新
        logger.info(f"Updated config: {section}.{option} = {value}")

    # 以写入模式打开配置文件，使用 UTF-8 编码
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        # 将配置信息写入文件
        config.write(f)

    # 记录信息日志，提示配置已保存到指定文件
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
