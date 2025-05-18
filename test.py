import cv2
import numpy as np
import matplotlib.pyplot as plt

def order_points(pts):
    # 对四个点进行排序：左上，右上，右下，左下
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # 左上
    rect[2] = pts[np.argmax(s)]  # 右下

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # 右上
    rect[3] = pts[np.argmax(diff)]  # 左下

    return rect

def four_point_transform(image, pts):
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
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # 计算透视变换矩阵并应用
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def scan_document(image_path):
    image = cv2.imread(image_path)
    orig = image.copy()
    ratio = image.shape[0] / 500.0
    image = cv2.resize(image, (int(image.shape[1] / ratio), 500))

    # 灰度化 + 边缘检测
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # 寻找轮廓
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            break
    else:
        raise ValueError("找不到文档轮廓")

    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

    # # 可选：灰度化 + 二值化（仿扫描效果）
    # warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    # scanned = cv2.adaptiveThreshold(warped_gray, 255,
    #                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                  cv2.THRESH_BINARY, 11, 2)

    return warped

# 示例使用
output = scan_document("test.png")
cv2.imwrite("scanned_output.jpg", output)

image_path="test.png"
original = cv2.imread(image_path)
if original is not None:
    processed = scan_document(image_path)

    # 显示原图与处理结果
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.title("Original Capture")
    plt.imshow(original_rgb)
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Processed Scan")
    plt.imshow(processed, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()
