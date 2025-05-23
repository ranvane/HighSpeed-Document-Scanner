import cv2
import numpy as np
from loguru import logger

def rotate_frame(image, frame_rotation):
    """
    根据frame_rotation的值旋转图像（仅支持0、90、180、270、360度）

    参数:
        image (numpy.ndarray): 输入的图像
        frame_rotation (int): 旋转角度，仅支持0、90、180、270、360

    返回:
        numpy.ndarray: 旋转后的图像

    异常:
        ValueError: 当frame_rotation不是0、90、180、270或360时抛出
        TypeError: 当frame_rotation不是整数类型时抛出
    """
    if frame_rotation == 0 or frame_rotation == 360:
        return image  # 无需旋转
    elif frame_rotation == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif frame_rotation == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif frame_rotation == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        raise ValueError("frame_rotation必须是0、90、180、270或360中的一个值")

def get_camera_max_resolution(camera_id=0):
    """
    获取指定摄像头的最大分辨率
    
    参数:
        camera_id: 摄像头设备ID (默认0)
    返回:
        width, height: 实际分辨率的宽度和高度
    """
    # 打开摄像头
    cap = cv2.VideoCapture(camera_id)

    # 设置为高分辨率（如果支持）
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

    # 获取实际分辨率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    logger.debug(f"摄像头 {camera_id} 最大支持分辨率: {width}x{height}")

    # 关闭摄像头
    cap.release()
    return width, height


def get_camera_resolution(camera_index=0):
    """
    获取指定摄像头的实际分辨率（宽度, 高度）

    参数:
        camera_index (int): 摄像头编号，默认是 0（主摄）

    返回:
        (width, height) 如果成功
        None 如果打开失败
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height


def set_camera_resolution(cap, width, height):
    """
    设置指定摄像头的分辨率
    参数:
        width (int): 要设置的宽度
        height (int): 要设置的高度
        camera_index (int): 摄像头编号，默认是 0（主摄）
    返回:
        True 如果成功
        False 如果打开失败
    """
    try:

        # 获取设置后的分辨率
        camera_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        camera_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        #计算最大分辨率的宽高比
        max_ratio = camera_width / camera_height

        # 计算高度
        _height = int(width / max_ratio)
        if _height != height:
            height = _height

        # 设置分辨率
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # 获取设置后的分辨率
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        

        # 检查设置是否成功
        if actual_width == width and actual_height == height:
            logger.info(f"成功设置摄像头分辨率为: {actual_width} x {actual_height}")
            return True
        else:
            logger.error(
                f"设置摄像头分辨率失败，当前分辨率为: {actual_width} x {actual_height}")
            return False
    except Exception as e:
        logger.error(f'{e}')


def count_cameras():
    '''
    检测电脑上的摄像头数量
    :return: 摄像头数量
    
    '''
    count = 0
    for i in range(10):  # 尝试前10个ID
        cap = cv2.VideoCapture(i)
        if not cap.read()[0]:
            break
        else:
            count += 1
        cap.release()
    return count


def get_camera_resolution_list(camera_index=0,
                               max_width=1920,
                               max_height=1080):
    """
    根据指定摄像头的分辨率列表，返回一个分辨率列表：从最大分辨率开始，直至720p。
    参数:
        camera_index (int): 摄像头编号，默认是 0（主摄）
        max_width (int): 最大宽度
        max_height (int): 最大高度
    返回:
        resolution_list (list): 分辨率列表，每个元素是一个元组 (width, height)  
    """
    # 初始化默认分辨率列表
    default_resolution_list = [(3264, 2448), (2592, 1994), (2048, 1536),
                               (1920, 1080), (1600, 1200), (1280, 960),
                               (1280, 720), (1024, 768), (800, 600),
                               (640, 480)]
    try:
        # 初始化默认分辨率宽度列表
        resolution_widths = [
            3264, 2592, 2048, 1920, 1600, 1280, 1024, 800, 640
        ]
        camera_width, camera_height = get_camera_max_resolution(camera_index)

        #计算最大分辨率的宽高比
        max_ratio = camera_width / camera_height
        # 初始化分辨率列表
        resolution_list = []

        for width in resolution_widths:
            # 计算高度
            height = int(width / max_ratio)
            # 检查分辨率是否在指定范围内
            if width <= camera_width:
                resolution_list.append((width, height))
            else:
                break
        if resolution_list == []:
            logger.debug(f"摄像头 返回默认分辨率列表: {default_resolution_list}")
            resolution_list = default_resolution_list
        return resolution_list
    except Exception as e:
        logger.debug(f"{e}摄像头 返回默认分辨率列表: {default_resolution_list}")
        default_resolution_list
def preprocess_image(img):
    """图像预处理：灰度转换、自适应直方图均衡化、自适应高斯模糊去噪"""
    # 灰度转换
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 自适应直方图均衡化
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # 计算图像标准差，自适应调整高斯模糊核大小
    std_dev = np.std(enhanced_gray)
    if std_dev < 20:
        kernel_size = (7, 7)
    elif std_dev < 50:
        kernel_size = (5, 5)
    else:
        kernel_size = (3, 3)

    # 自适应高斯模糊去噪
    blurred = cv2.GaussianBlur(enhanced_gray, kernel_size, 0)
    return enhanced_gray, blurred

def detect_edges(blurred):
    """
    边缘检测：使用自适应 Canny 算法提取图像边缘

    Args:
        blurred (numpy.ndarray): 经过模糊处理后的图像

    Returns:
        numpy.ndarray: 经过边缘检测和形态学膨胀操作后的图像
    """
    # 计算图像的中位数，用于后续自适应阈值的计算
    median = np.median(blurred)

    # 依据中位数计算 Canny 边缘检测的高低阈值
    # 下限阈值为中位数的 67%，且不小于 0
    lower = int(max(0, (1.0 - 0.33) * median))
    # 上限阈值为中位数的 133%，且不大于 255
    upper = int(min(255, (1.0 + 0.33) * median))

    # 使用计算得到的自适应阈值进行 Canny 边缘检测
    edges = cv2.Canny(blurred, lower, upper)

    # 定义一个 3x3 的结构元素，用于形态学膨胀操作
    kernel = np.ones((3, 3), np.uint8)
    # 对边缘图像进行形态学膨胀操作，连接断开的边缘
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    return dilated_edges

def find_document_contour(edges, original_img):
    """
    轮廓检测与筛选：找到最可能的纸张轮廓

    参数:
        edges (numpy.ndarray): 经过边缘检测后的图像，包含图像的边缘信息
        original_img (numpy.ndarray): 原始输入图像，用于在其上绘制轮廓
        draw_contours (bool): 是否在原始图像上绘制检测到的轮廓，默认为 False

    返回:
        document_contour (numpy.ndarray): 最可能的纸张轮廓，如果未找到则为 None
        img_with_contours (numpy.ndarray): 带有绘制轮廓(取决于draw_contours)的原始图像副本
    """
    # 查找轮廓
    # 使用 cv2.findContours 函数在边缘图像中查找外部轮廓
    # cv2.RETR_EXTERNAL 表示只检测外部轮廓
    # cv2.CHAIN_APPROX_SIMPLE 表示压缩水平、垂直和对角方向的冗余点
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    # 按面积降序排序轮廓，面积大的轮廓排在前面
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # 初始化文档轮廓为 None，表示尚未找到合适的轮廓
    document_contour = None
    # 复制原始图像，避免在原始图像上直接操作
    img_with_contours = original_img.copy()

    # 自适应计算面积阈值，根据图像大小调整
    # 获取原始图像的高度和宽度
    height, width = original_img.shape[:2]
    # 最小面积阈值设置为图像总面积的 1%，可根据实际情况调整比例
    min_area_threshold = 0.01 * height * width

    # 遍历轮廓，筛选最可能的纸张轮廓
    for contour in contours:
        # 计算当前轮廓的面积
        area = cv2.contourArea(contour)
        # 如果轮廓面积小于最小面积阈值，则跳过该轮廓
        if area < min_area_threshold:
            continue

        # 自适应计算多边形近似精度，根据轮廓周长调整
        # 多边形近似精度设置为轮廓周长的 2%
        epsilon = 0.02 * cv2.arcLength(contour, True)
        # 使用多边形逼近方法对轮廓进行近似，减少轮廓的点数
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 筛选条件：轮廓为四边形，且面积足够大
        if len(approx) == 4:
            # 找到符合条件的四边形轮廓，将其作为文档轮廓
            document_contour = approx
            break

    # 返回找到的轮廓（若存在）
    if document_contour is not None:
        return document_contour
    else:
        return None

def draw_boxes_on_image(frame, boxes, color=(0, 255, 0), thickness=5):
    """
    在图像上绘制多个方框
    参数:
        img (numpy.ndarray): 输入图像
        boxes (list): 包含多个方框的列表，每个方框由四个点的坐标组成
        color (tuple): 方框的颜色，默认为绿色 (0, 255, 0)
        thickness (int): 方框的线宽，默认为 2
    返回:
        img_with_boxes (numpy.ndarray): 带有绘制方框的图像
    """
    cv2.drawContours(frame, [boxes], -1, (0, 0, 255), 5)
    return frame

def detect_contour(frame):
    """
    检测图像中的方框并绘制面积最大的边界框
    :param frame: 输入图像帧
    :return: 带有边界框的图像帧
    """
    # 1. 图像预处理
    _,blurred = preprocess_image(frame)

    # 2. 边缘检测
    edged=detect_edges(blurred)

    # 查找轮廓
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # 3. 轮廓检测与筛选
    document_contour = find_document_contour(edged, frame)



    return document_contour,frame


def order_points(pts):
    """
    对四个点进行排序：左上，右上，右下，左下

    参数:
        pts (numpy.ndarray): 输入的四个点的坐标

    返回:
        rect (numpy.ndarray): 排序后的四个点的坐标
    """
    # 初始化一个形状为 (4, 2) 的零矩阵，数据类型为 float32，用于存储排序后的四个点的坐标
    rect = np.zeros((4, 2), dtype="float32")

    # 计算每个点的 x 坐标和 y 坐标之和，存储在 s 数组中
    # 左上点的 x 和 y 坐标之和通常最小，右下点的 x 和 y 坐标之和通常最大
    s = pts.sum(axis=1)
    # 将和最小的点作为左上点，赋值给 rect 数组的第一个元素
    rect[0] = pts[np.argmin(s)]
    # 将和最大的点作为右下点，赋值给 rect 数组的第三个元素
    rect[2] = pts[np.argmax(s)]

    # 计算每个点的 x 坐标和 y 坐标之差，存储在 diff 数组中
    # 右上点的 x - y 差值通常最小，左下点的 x - y 差值通常最大
    diff = np.diff(pts, axis=1)
    # 将差值最小的点作为右上点，赋值给 rect 数组的第二个元素
    rect[1] = pts[np.argmin(diff)]
    # 将差值最大的点作为左下点，赋值给 rect 数组的第四个元素
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    """
    对图像进行透视变换

    参数:
        image (numpy.ndarray): 输入图像
        pts (numpy.ndarray): 四个点的坐标

    返回:
        warped (numpy.ndarray): 透视变换后的图像
    """
    # 对四个点进行排序：左上，右上，右下，左下
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # 计算目标图像的宽度和高度
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    # 构建目标图像的坐标
    dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1],
                    [0, maxHeight - 1]],
                   dtype="float32")

    # 计算透视变换矩阵并应用
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def transform_document(frame):
    """
    扫描文档并进行透视变换

    参数:
        image_path (str): 图像文件路径

    返回:
        warped (numpy.ndarray): 透视变换后的图像
    """
    # 1. 图像预处理
    _, blurred = preprocess_image(frame)

    # 2. 边缘检测
    edged = detect_edges(blurred)


    # 3. 轮廓检测与筛选
    document_contour = find_document_contour(edged, frame)

    # 4. 对原始图像进行透视变换（检查是否找到文档轮廓）
    if document_contour is not None:
        # 调整轮廓的形状，使其符合 four_point_transform 函数的输入要求
        pts = document_contour.reshape(4, 2)
        # 对原始图像进行透视变换
        warped = four_point_transform(frame, pts)
    else:
        # 若未找到合适轮廓，返回原始图像
        logger.warning("未找到合适的文档轮廓，返回原始图像")
        warped = frame

    return warped


if __name__ == "__main__":
    print(count_cameras())

    set_camera_resolution(1920, 1440)
