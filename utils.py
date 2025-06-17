import wx
import os
import cv2
from loguru import logger
from PIL import Image
from datetime import datetime
from app_config import get_config, save_config
def get_save_path(suffix="jpg"):
    """
    根据配置生成带时间戳的文件保存路径。

    参数:
        suffix (str): 文件后缀名（默认为 'pdf'）

    返回:
        str: 完整的文件保存路径
    """
    # 从配置中获取保存路径
    config=get_config()
    save_location = config.get('PATHS', 'save_location')
    # 从配置中获取保存文件命名格式
    naming_format = config.get('PATHS', 'save_naming_format')
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime(naming_format)
    file_name = f"{timestamp}.{suffix}"

    # 确保保存路径存在
    os.makedirs(save_location, exist_ok=True)

    # 构建保存文件的完整路径
    path = os.path.join(save_location, file_name)

    logger.info(f"生成保存路径: {path}")
    return path

def save_image(frame, path):
    """
    保存捕获的图像到指定路径。

    参数:
        frame (np.ndarray): OpenCV BGR 格式的图像帧。
        path (str): 图像文件的完整保存路径。
    """
    try:
        # 将 BGR 格式的 OpenCV 图像转换为 RGB 格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 创建 wx.Image 对象
        image = wx.Image(rgb_frame.shape[1], rgb_frame.shape[0])
        image.SetData(rgb_frame.tobytes())
        # 保存图像到指定路径
        logger.info(f"保存图像: {path}")
        image.SaveFile(path, wx.BITMAP_TYPE_JPEG)
    except Exception as e:
        logger.error(f"保存图像失败: {e}")

def save_pdf(frame, path, dpi=300):
    """
    通过 PIL 保存为 PDF。

    参数:
        frames (list of np.ndarray): OpenCV BGR 格式的图像帧列表。
        path (str): PDF 文件的保存路径。
        dpi (int): 输出 PDF 的 DPI。
    """
    try:

        # 转换为 RGB 并创建 PIL 图像对象
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_frame)  # 自动识别为 RGB


        # 保存为 PDF（第一张图为基准）
        pil_img.save(path, save_all=True, append_images=pil_img, resolution=dpi)

        logger.info(f"PDF 文件已成功保存至: {path}")

    except Exception as e:
        logger.exception(f"生成 PDF 失败: {e}")

def save_multip_pdf(image_paths, output_path, dpi=300):
    """
    将多张图片合并为一个多页 PDF 文件，支持设置 DPI。

    参数:
    - image_paths: 图片路径列表（如 ['img1.png', 'img2.jpg', ...]）
    - output_path: 输出 PDF 文件路径（如 'output.pdf'）
    - dpi: 输出 PDF 的每英寸点数，决定图像在 PDF 中的实际尺寸（默认 300）
    """
    try:
        if not image_paths:
            raise ValueError("图片路径列表为空！")

        images = []
        for path in image_paths:
            img = Image.open(path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)

        # 保存 PDF，设置 dpi（通过 resolution 参数）
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            resolution=dpi
        )

        logger.info(f"PDF 文件已成功保存至: {output_path}")
    except Exception as e:
        logger.exception(f"生成 PDF 失败: {e}")
