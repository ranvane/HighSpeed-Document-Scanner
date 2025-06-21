import wx
import os
import cv2
import numpy as np
from loguru import logger
import time
from loguru import logger
from PIL import Image
from datetime import datetime
from app_config import get_config, save_config
# 定义一个装饰器，用于计算函数的执行时间
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        exec_time = end_time - start_time
        print(f"{func.__name__} 执行时间: {exec_time:.4f} 秒")
        return result
    return wrapper
def get_save_path(suffix="jpg",group_name=None,prefix=None):
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
    # 拼接文件名
    if prefix:
        file_name = f"{prefix}_{timestamp}.{suffix}"
    else:
        file_name = f"{timestamp}.{suffix}"

    # 生成保存文件的完整路径
    if group_name:
        save_location = os.path.join(save_location, group_name)
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

def merge_images(image_paths, output_path, direction='vertical', target_size=None, padding=10, bg_color=(255, 255, 255)):
    """
    将多张图片合并为一张长图（支持纵向/横向、统一宽高、边距）并保存。

    参数:
    - image_paths: 图片路径列表
    - output_path: 合并后的输出路径
    - direction: 'vertical' 或 'horizontal'，默认 'vertical'
    - target_size: 统一宽度或高度，单位：像素。例如 target_size=600，
        - 如果 direction='vertical'，则统一宽度
        - 如果 direction='horizontal'，则统一高度
    - padding: 每张图片之间的间距（像素）
    - bg_color: 背景颜色 (R, G, B)，默认白色
    """
    if not image_paths:
        raise ValueError("图片路径列表为空！")

    try:
        # 打开图片
        images = []
        for path in image_paths:
            try:
                img = Image.open(path).convert("RGB")
                images.append(img)
            except Exception as e:
                print(f"跳过无法打开的图片: {path}，错误: {e}")

        if not images:
            raise RuntimeError("没有可用的图片进行合并。")

        # 可选缩放：统一宽度或高度
        if target_size is not None:
            resized_images = []
            for img in images:
                if direction == 'vertical':
                    # 统一宽度，等比缩放高度
                    w_percent = target_size / img.width
                    new_height = int(img.height * w_percent)
                    resized = img.resize((target_size, new_height), Image.LANCZOS)
                elif direction == 'horizontal':
                    # 统一高度，等比缩放宽度
                    h_percent = target_size / img.height
                    new_width = int(img.width * h_percent)
                    resized = img.resize((new_width, target_size), Image.LANCZOS)
                else:
                    raise ValueError("参数 direction 必须为 'vertical' 或 'horizontal'")
                resized_images.append(resized)
            images = resized_images

        # 计算合并后图片尺寸
        if direction == 'vertical':
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images) + padding * (len(images) - 1)
            merged_image = Image.new("RGB", (max_width, total_height), bg_color)

            y = 0
            for img in images:
                merged_image.paste(img, ((max_width - img.width) // 2, y))
                y += img.height + padding

        elif direction == 'horizontal':
            max_height = max(img.height for img in images)
            total_width = sum(img.width for img in images) + padding * (len(images) - 1)
            merged_image = Image.new("RGB", (total_width, max_height), bg_color)

            x = 0
            for img in images:
                merged_image.paste(img, (x, (max_height - img.height) // 2))
                x += img.width + padding

        else:
            raise ValueError("参数 direction 只能为 'vertical' 或 'horizontal'")

        merged_image.save(output_path)
        print(f"图片合并成功，保存为: {output_path}")

    except Exception as e:
        print(f"图片合并失败: {e}")


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
        pil_img.save(path, append_images=pil_img, resolution=dpi)

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


class SCRFD():
    def __init__(self, onnxmodel, confThreshold=0.6, nmsThreshold=0.5):
        """
        初始化 SCRFD 类的实例。

        :param onnxmodel: ONNX 模型文件的路径
        :param confThreshold: 分类置信度阈值，默认为 0.5
        :param nmsThreshold: 非极大值抑制（NMS）的 IoU 阈值，默认为 0.5
        """
        # 输入图像的宽度
        self.inpWidth = 640
        # 输入图像的高度
        self.inpHeight = 640
        # 分类置信度阈值，用于过滤低置信度的检测结果
        self.confThreshold = confThreshold
        # 非极大值抑制的 IoU 阈值，用于去除重叠的检测框
        self.nmsThreshold = nmsThreshold
        # 加载 ONNX 模型
        self.net = cv2.dnn.readNet(onnxmodel)
        # 是否保持图像的宽高比，默认为 True
        self.keep_ratio = True
        # 特征金字塔网络（FPN）的特征图数量
        self.fmc = 3
        # FPN 各层的特征步长
        self._feat_stride_fpn = [8, 16, 32]
        # 每个位置的锚框数量
        self._num_anchors = 4

    def resize_image(self, srcimg):
        """
        调整输入图像的大小，根据是否保持宽高比进行不同处理，并在需要时添加边框。

        :param srcimg: 输入的原始图像
        :return: 调整大小后的图像，以及新的高度、宽度和上下左右的填充量
        """
        # 初始化填充量和新的高度、宽度
        padh, padw, newh, neww = 0, 0, self.inpHeight, self.inpWidth
        # 检查是否需要保持宽高比且图像的高度和宽度不相等
        if self.keep_ratio and srcimg.shape[0] != srcimg.shape[1]:
            # 计算图像的高宽比
            hw_scale = srcimg.shape[0] / srcimg.shape[1]
            if hw_scale > 1:
                # 高度大于宽度，调整宽度以保持宽高比
                newh, neww = self.inpHeight, int(self.inpWidth / hw_scale)
                # 调整图像大小
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                # 计算左右填充量
                padw = int((self.inpWidth - neww) * 0.5)
                # 添加左右边框
                img = cv2.copyMakeBorder(img, 0, 0, padw, self.inpWidth - neww - padw, cv2.BORDER_CONSTANT,
                                         value=0)
            else:
                # 宽度大于高度，调整高度以保持宽高比
                newh, neww = int(self.inpHeight * hw_scale) + 1, self.inpWidth
                # 调整图像大小
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                # 计算上下填充量
                padh = int((self.inpHeight - newh) * 0.5)
                # 添加上下边框
                img = cv2.copyMakeBorder(img, padh, self.inpHeight - newh - padh, 0, 0, cv2.BORDER_CONSTANT, value=0)
        else:
            # 不保持宽高比，直接调整图像到指定大小
            img = cv2.resize(srcimg, (self.inpWidth, self.inpHeight), interpolation=cv2.INTER_AREA)
        return img, newh, neww, padh, padw

    def distance2bbox(self, points, distance, max_shape=None):
        """
        根据中心点坐标和偏移量计算边界框的坐标。

        :param points: 中心点坐标数组，形状为 (N, 2)，N 为点的数量，每个点包含 (x, y) 坐标
        :param distance: 偏移量数组，形状为 (N, 4)，每个点的偏移量依次为 (left, top, right, bottom)
        :param max_shape: 可选参数，图像的最大形状 (height, width)，用于限制边界框坐标在图像范围内
        :return: 边界框坐标数组，形状为 (N, 4)，每个边界框包含 (x1, y1, x2, y2) 坐标
        """
        # 计算边界框左上角的 x 坐标，通过中心点 x 坐标减去左偏移量
        x1 = points[:, 0] - distance[:, 0]
        # 计算边界框左上角的 y 坐标，通过中心点 y 坐标减去上偏移量
        y1 = points[:, 1] - distance[:, 1]
        # 计算边界框右下角的 x 坐标，通过中心点 x 坐标加上右偏移量
        x2 = points[:, 0] + distance[:, 2]
        # 计算边界框右下角的 y 坐标，通过中心点 y 坐标加上下偏移量
        y2 = points[:, 1] + distance[:, 3]
        # 如果提供了图像的最大形状，则对边界框坐标进行裁剪，确保坐标在图像范围内
        if max_shape is not None:
            # 限制 x1 坐标在 [0, max_shape[1]] 范围内
            x1 = np.clip(x1, 0, max_shape[1])
            # 限制 y1 坐标在 [0, max_shape[0]] 范围内
            y1 = np.clip(y1, 0, max_shape[0])
            # 限制 x2 坐标在 [0, max_shape[1]] 范围内
            x2 = np.clip(x2, 0, max_shape[1])
            # 限制 y2 坐标在 [0, max_shape[0]] 范围内
            y2 = np.clip(y2, 0, max_shape[0])
        # 将计算得到的边界框坐标按列堆叠成一个数组返回
        return np.stack([x1, y1, x2, y2], axis=-1)

    def distance2kps(self, points, distance, max_shape=None):
        """
        根据中心点坐标和偏移量计算关键点的坐标。

        :param points: 中心点坐标数组，形状为 (N, 2)，N 为点的数量，每个点包含 (x, y) 坐标
        :param distance: 偏移量数组，形状为 (N, M)，M 是关键点偏移量的总数，每两个值对应一个关键点的 (x, y) 偏移量
        :param max_shape: 可选参数，图像的最大形状 (height, width)，用于限制关键点坐标在图像范围内
        :return: 关键点坐标数组，形状为 (N, M//2, 2)
        """
        # 存储关键点坐标的列表
        preds = []
        # 遍历偏移量数组，每两个值为一组，代表一个关键点的 (x, y) 偏移量
        for i in range(0, distance.shape[1], 2):
            # 计算关键点的 x 坐标，通过中心点 x 坐标加上对应的 x 偏移量
            px = points[:, i % 2] + distance[:, i]
            # 计算关键点的 y 坐标，通过中心点 y 坐标加上对应的 y 偏移量
            py = points[:, i % 2 + 1] + distance[:, i + 1]
            # 如果提供了图像的最大形状，则对关键点坐标进行裁剪，确保坐标在图像范围内
            if max_shape is not None:
                # 注意：原代码使用了 PyTorch 的 clamp 方法，这里修正为 NumPy 的 clip 方法
                px = np.clip(px, 0, max_shape[1])
                py = np.clip(py, 0, max_shape[0])
            # 将计算得到的关键点 x 坐标添加到列表中
            preds.append(px)
            # 将计算得到的关键点 y 坐标添加到列表中
            preds.append(py)
        # 将关键点坐标列表按列堆叠成一个数组返回
        return np.stack(preds, axis=-1)

    @measure_time
    def detect(self, srcimg):
        """
        对输入图像进行目标检测，返回绘制后的图片和检测目标四个角点的坐标。

        :param srcimg: 输入的原始图像
        :return: 包含绘制后的图片和检测目标四个角点坐标列表的列表，格式为 [outimg, corner_points_list]
        """
        # 调整输入图像的大小，并获取调整后的图像信息和填充量
        img, newh, neww, padh, padw = self.resize_image(srcimg)
        # 将调整后的图像转换为适合网络输入的 blob 格式
        blob = cv2.dnn.blobFromImage(img, 1.0 / 128, (self.inpWidth, self.inpHeight), (127.5, 127.5, 127.5),
                                     swapRB=True)
        # 将 blob 数据设置为网络的输入
        self.net.setInput(blob)

        # 执行前向传播，获取网络输出层的输出结果
        outs = self.net.forward(self.net.getUnconnectedOutLayersNames())

        # 初始化存储得分、边界框和关键点的列表
        scores_list, bboxes_list, kpss_list = [], [], []
        # 遍历特征金字塔网络（FPN）各层的特征步长
        for idx, stride in enumerate(self._feat_stride_fpn):
            # 获取当前层的分类得分
            scores = outs[idx * self.fmc][0]
            # 获取当前层的边界框预测结果，并乘以步长进行缩放
            bbox_preds = outs[idx * self.fmc + 1][0] * stride
            # 获取当前层的关键点预测结果，并乘以步长进行缩放
            kps_preds = outs[idx * self.fmc + 2][0] * stride
            # 计算当前层特征图的高度
            height = blob.shape[2] // stride
            # 计算当前层特征图的宽度
            width = blob.shape[3] // stride
            # 生成锚框的中心点坐标
            anchor_centers = np.stack(np.mgrid[:height, :width][::-1], axis=-1).astype(np.float32)
            # 将锚框中心点坐标乘以步长，并调整形状
            anchor_centers = (anchor_centers * stride).reshape((-1, 2))
            # 如果每个位置的锚框数量大于 1，扩展锚框中心点坐标
            if self._num_anchors > 1:
                anchor_centers = np.stack([anchor_centers] * self._num_anchors, axis=1).reshape((-1, 2))

            # 找出得分大于等于置信度阈值的索引

            pos_inds = np.where(scores >= self.confThreshold)[0]
            # 根据锚框中心点和边界框预测结果计算边界框坐标
            bboxes = self.distance2bbox(anchor_centers, bbox_preds)
            # 获取满足条件的得分
            pos_scores = scores[pos_inds]
            # 获取满足条件的边界框
            pos_bboxes = bboxes[pos_inds]
            # 将满足条件的得分添加到列表中
            scores_list.append(pos_scores)
            # 将满足条件的边界框添加到列表中
            bboxes_list.append(pos_bboxes)

            # 根据锚框中心点和关键点预测结果计算关键点坐标
            kpss = self.distance2kps(anchor_centers, kps_preds)
            # 调整关键点坐标的形状
            kpss = kpss.reshape((kpss.shape[0], -1, 2))
            # 获取满足条件的关键点
            pos_kpss = kpss[pos_inds]
            # 将满足条件的关键点添加到列表中
            # 关键点信息（kpss），这些关键点通常是目标对象的特征点（例如人脸的关键点、文档的四个顶点等）。
            kpss_list.append(pos_kpss)

        # 将所有得分合并为一维数组
        scores = np.vstack(scores_list).ravel()
        # 将所有边界框合并
        bboxes = np.vstack(bboxes_list)
        # 将所有关键点合并
        kpss = np.vstack(kpss_list)
        # 将边界框的右下角坐标转换为宽高
        bboxes[:, 2:4] = bboxes[:, 2:4] - bboxes[:, 0:2]
        # 计算高度和宽度的缩放比例
        ratioh, ratiow = srcimg.shape[0] / newh, srcimg.shape[1] / neww
        # 将边界框的坐标转换回原始图像的坐标
        bboxes[:, 0] = (bboxes[:, 0] - padw) * ratiow
        bboxes[:, 1] = (bboxes[:, 1] - padh) * ratioh
        bboxes[:, 2] = bboxes[:, 2] * ratiow
        bboxes[:, 3] = bboxes[:, 3] * ratioh
        # 将关键点的坐标转换回原始图像的坐标
        kpss[:, :, 0] = (kpss[:, :, 0] - padw) * ratiow
        kpss[:, :, 1] = (kpss[:, :, 1] - padh) * ratioh
        # 使用非极大值抑制（NMS）过滤重叠的边界框
        indices = cv2.dnn.NMSBoxes(bboxes.tolist(), scores.tolist(), self.confThreshold, self.nmsThreshold)
        # 将 indices 转换为一维数组
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()

        corner_points_list = []

        # 使用关键点作为角点
        for i in indices:
            keypoints = kpss[i]  # shape: (num_keypoints, 2)
            # 假设关键点顺序为 [左上, 右上, 右下, 左下]
            corner_points = [(int(kp[0]), int(kp[1])) for kp in keypoints[:4]]  # 提取前4个关键点
            corner_points = order_corner_points(corner_points)  # 顺序化[左上, 右上, 右下, 左下]
            corner_points_list.append(corner_points)
        #
        #     # 可选：绘制关键点连线
        #     for j in range(4):
        #         start_point = corner_points[j]
        #         end_point = corner_points[(j + 1) % 4]
        #         cv2.line(srcimg, start_point, end_point, (255, 0, 0), 2)

        # 将 BGR 格式转换为 RGB 格式，因为 matplotlib 使用 RGB
        outimg = cv2.cvtColor(srcimg, cv2.COLOR_BGR2RGB)
        return outimg, corner_points_list

def order_corner_points(pts):
    """
    将无序的四个角点排序为:
    [左上, 右上, 右下, 左下]

    参数:
    pts (list of lists): 包含四个角点坐标的列表，每个角点是一个长度为2的列表。

    返回:
    list of lists: 排序后的四个角点坐标的列表。
    """
    # 将角点列表转换为float32类型的NumPy数组，以便进行后续的计算
    pts = np.array(pts, dtype="float32")

    # 初始化一个4x2的零矩阵，用于存储排序后的角点坐标
    rect = np.zeros((4, 2), dtype="float32")

    # 计算每个角点坐标的和，以此来确定左上和右下角点
    s = pts.sum(axis=1)
    # 找到和最小的角点，即为左上角点
    rect[0] = pts[np.argmin(s)]
    # 找到和最大的角点，即为右下角点
    rect[2] = pts[np.argmax(s)]

    # 计算每个角点坐标的差，以此来确定左下和右上角点
    diff = np.diff(pts, axis=1)
    # 找到差最大的角点，即为左下角点
    rect[3] = pts[np.argmax(diff)]
    # 找到差最小的角点，即为右上角点
    rect[1] = pts[np.argmin(diff)]

    # 将排序后的角点坐标转换为整数类型，并返回其列表形式
    return rect.astype(int).tolist()
