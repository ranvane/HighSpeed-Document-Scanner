import wx
import cv2
from loguru import logger
import img2pdf
from PIL import Image
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



def save_pdf(frames, path, dpi=300):
    """
    通过 PIL 保存为 PDF。

    参数:
        frames (list of np.ndarray): OpenCV BGR 格式的图像帧列表。
        path (str): PDF 文件的保存路径。
        dpi (int): 输出 PDF 的 DPI。
    """
    try:
        pil_images = []

        for i, frame in enumerate(frames):
            # 转换为 RGB 并创建 PIL 图像对象
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)  # 自动识别为 RGB
            pil_images.append(pil_img)

        if not pil_images:
            logger.error("没有有效的图像帧可以保存为 PDF")
            return

        # 保存为 PDF（第一张图为基准）
        pil_images[0].save(path, save_all=True, append_images=pil_images[1:], resolution=dpi)

        logger.info(f"PDF 文件已成功保存至: {path}")

    except Exception as e:
        logger.exception(f"生成 PDF 失败: {e}")
