import cv2
import numpy as np
from loguru import logger


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


def detect_and_draw_boxes(frame):
    """
    检测图像中的方框并绘制面积最大的边界框
    :param frame: 输入图像帧
    :return: 带有边界框的图像帧
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # 查找轮廓
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # 初始化最大面积和对应的边界框
    max_area = 0
    max_rect = None

    # 遍历每个轮廓
    for contour in contours:
        # 计算轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        # 更新最大面积和对应的边界框
        if area > max_area:
            max_area = area
            max_rect = (x, y, w, h)

    # 绘制面积最大的边界框
    if max_rect is not None:
        x, y, w, h = max_rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame


def order_points(pts):
    """
    对四个点进行排序：左上，右上，右下，左下

    参数:
        pts (numpy.ndarray): 输入的四个点的坐标

    返回:
        rect (numpy.ndarray): 排序后的四个点的坐标
    """
    # 初始化一个4x2的零矩阵，用于存储排序后的点
    rect = np.zeros((4, 2), dtype="float32")

    # 计算每个点的和（x + y），用于找到左上和右下点
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # 左上
    rect[2] = pts[np.argmax(s)]  # 右下

    # 计算每个点的差（x - y），用于找到右上和左下点
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # 右上
    rect[3] = pts[np.argmax(diff)]  # 左下

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


def transform_document(image_path):
    """
    扫描文档并进行透视变换

    参数:
        image_path (str): 图像文件路径

    返回:
        warped (numpy.ndarray): 透视变换后的图像
    """
    # 读取图像
    image = cv2.imread(image_path)
    orig = image.copy()
    ratio = image.shape[0] / 500.0
    image = cv2.resize(image, (int(image.shape[1] / ratio), 500))

    # 灰度化 + 边缘检测
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # 寻找轮廓
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST,
                                   cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for c in contours:
        # 计算轮廓的周长
        peri = cv2.arcLength(c, True)
        # 使用多边形逼近方法对轮廓进行近似
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # 检查近似多边形的顶点数是否为4
        if len(approx) == 4:
            screenCnt = approx
            break
    else:
        logger.error("找不到文档轮廓")
        return None

    # 对原始图像进行透视变换
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

    return warped


if __name__ == "__main__":
    print(count_cameras())

    set_camera_resolution(1920, 1440)
