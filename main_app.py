import wx
import os
import threading
import time
import numpy as np
import cv2
# 从自定义模块中导入主用户界面框架类
from Document_Scanner_UI import Main_Ui_Frame
# 从自定义摄像头工具模块中导入使用的函数
from cammer_utils import get_camera_resolution, get_camera, rotate_frame, count_cameras, detect_contour, get_camera_supported_resolutions, draw_boxes_on_image, transform_document
from loguru import logger
from app_config import get_config, save_config,update_os_and_save_path
# 从自定义配置界面模块中导入配置窗口类
from config_ui import ConfigFrame  # 这是一个自定义的配置窗口类
from datetime import datetime
from utils import save_image,merge_images,save_pdf,save_multip_pdf,get_save_path,SCRFD,measure_time


# 获取当前脚本所在的目录
base_dir = os.path.dirname(os.path.abspath(__file__))

class Main_Frame(Main_Ui_Frame):
    """
    主应用程序框架类，继承自 Main_Ui_Frame。
    负责管理摄像头操作、用户界面交互以及配置管理等功能。
    """

    def __init__(self):
        """
        初始化主应用程序框架。
        初始化摄像头相关参数、配置信息和用户界面元素。
        根据配置文件选择使用本地摄像头或网络摄像头，并启动相应的摄像头。
        """
        super().__init__(parent=None)
        self.debug = True # 是否开启调试模式
        self.update_frame_debug=False # 是否更新帧调试信息

        # 摄像头索引，初始化为 -1
        self.local_camera_index = -1
        # 是否使用网络摄像头，初始化为 False
        self.use_webcam = False
        # 网络摄像头的 IP 地址，初始为空字符串
        self.webcam_url = ''
        # 摄像头分辨率，初始为 None
        self.camera_resolution = None
        # 摄像头帧率，初始为 30
        self.fps = 30
        # 当前捕获的帧，初始为 None
        self.current_captured_frame = None
        # 摄像头捕获对象，初始为 None
        self.camera_capture = None
        # 摄像头捕获线程，初始为 None
        self.capture_thread = None
        # update_bitmap中画布缓存，初始为 None
        self.canvas_cache = None

        # 设置默认分辨率(优先选择 1920x1440)
        self.PREFERRED_RESOLUTION = (1920, 1440)

        # 摄像头支持的所有分辨率列表，初始为空列表
        self.camera_supported_resolutions = []

        # 控制摄像头捕获线程运行状态的标志位，初始为 False
        self.is_camera_capture_running = False
        # 控制是否启用方框检测的标志位，初始为 False
        self.is_document_outline_detection_enabled = False
        # 控制是否启用曲面展平的标志位，初始为 False
        self.is_surface_rectification_enabled = False
        # 设置曲面展平复选框的初始值
        self.m_checkBox_rectify_surface.SetValue(self.is_surface_rectification_enabled)
        # 图像旋转角度，初始为 0 度
        self.image_rotation = 0
        # 初始化配置信息
        self.config = get_config()
        # 缩略图最大尺寸
        self.thumb_max_size=(256, 256)
        update_os_and_save_path()# 根据系统更新操作系统、默认保存路径信息

        # 定义 ONNX 模型文件的路径
        onnxmodel = 'models/cv_resnet18_card_correction.onnx'
        # 创建 SCRFD 类的实例，传入 ONNX 模型路径、置信度阈值和 NMS 阈值
        self.card_net = SCRFD(onnxmodel)

        # 打印是否使用 USB 摄像头的配置信息
        logger.debug(self.config.getboolean('CAMERA', 'use_usb_camera'))
        # 打印是否使用 USB 摄像头的配置信息
        logger.debug(self.config.getboolean('CAMERA', 'use_usb_camera'))
        if not self.config.getboolean('CAMERA', 'use_usb_camera'):
            self.switch_to_local_camera()
        else:
            self.switch_to_web_camera()
    
    def clear_camera_bitmap(self):
        """
        清空 m_bitmap_camera 显示的图像
        """
        # 创建一个空白的 wx.Bitmap 对象
        blank_bitmap = wx.Bitmap(1, 1)
        self.bitmap=blank_bitmap
        # self.m_bitmap_camera.SetBitmap(blank_bitmap)
        # self.m_bitmap_camera.Refresh()
    def _update_camera_ui(self, show_local):
        """
        更新摄像头相关的 UI 显示状态

        Args:
            show_local (bool): 是否显示本地摄像头相关控件
        """
        parent_sizer = self.m_comboBox_select_camera.GetContainingSizer()
        if parent_sizer:
            if show_local:
                parent_sizer.Show(self.m_comboBox_select_camera)
                parent_sizer.Show(self.m_comboBox_select_camera_resolution)
                parent_sizer.Hide(self.m_web_camera_address)
                logger.info("已切换到本地摄像头模式")
                self.m_checkBox_show_camera2_image.Enable(True)
                self.m_checkBox_web_camera.SetValue(False)
            else:
                parent_sizer.Hide(self.m_comboBox_select_camera)
                parent_sizer.Hide(self.m_comboBox_select_camera_resolution)
                parent_sizer.Show(self.m_web_camera_address)
                if len(self.m_web_camera_address.GetValue())<1:
                    self.m_web_camera_address.SetValue(self.config.get('CAMERA', 'ip_address'))
                logger.info("已切换到网络摄像头模式")
                self.m_checkBox_show_camera2_image.Enable(False)
                self.m_checkBox_web_camera.SetValue(True)
            parent_sizer.Layout()


    def switch_to_local_camera(self):
        """切换到本地摄像头模式"""
        self.use_webcam = False
        # 清空 m_bitmap_camera 图像
        self.clear_camera_bitmap()
        logger.debug("启动切换到本地摄像头模式")
        self._update_camera_ui(show_local=True)
        wx.CallAfter(self.start_camera)

    def switch_to_web_camera(self):
        """切换到网络摄像头模式"""
        self.use_webcam = True
        # 清空 m_bitmap_camera 图像
        self.clear_camera_bitmap()
        logger.debug("启动切换到网络摄像头模式")
        self._update_camera_ui(show_local=False)
        wx.CallAfter(self.start_camera)

    def on_use_webcam(self, event):
        """
        切换使用网络摄像头状态。
        根据复选框状态切换使用本地摄像头或网络摄像头，并更新相应的 UI 控件。

        Args:
            event: 触发事件的事件对象
        """
        self.use_webcam = not self.use_webcam
        logger.info("切换摄像头模式")

        if self.use_webcam:
            self.switch_to_web_camera()
        else:
            self.switch_to_local_camera()

    def init_web_camera(self):
        """
        初始化网络摄像头设备。

        功能：
            1. 从 UI 输入框获取网络摄像头地址。
            2. 尝试连接网络摄像头并检测其是否可用。
            3. 若连接成功，将摄像头捕获对象赋值给 self.camera_capture。

        Returns:
            None
        """
        # self.m_web_camera_address.SetValue(self.config.get('CAMERA', 'ip_address'))# 读取网络摄像头地址,并设置到文本框中
        self.webcam_url = self.m_web_camera_address.GetValue()
        logger.info(f"网络摄像头地址: {self.webcam_url}")
        # 检查网络摄像头是否可用
        if self.webcam_url:
            try:
                logger.info(f"尝试连接网络摄像头: {self.webcam_url}")
                # 尝试连接网络摄像头
                capture = cv2.VideoCapture(self.webcam_url)
                if capture.isOpened():
                    self.camera_capture = capture
                else:
                    logger.error(f"无法连接网络摄像头: {self.webcam_url}")
            except Exception as e:
                logger.error(f"无法连接网络摄像头: {self.webcam_url}")

    def init_local_camera(self):
        """
        初始化本地摄像头设备。
        功能：
            1. 检测可用摄像头数量。
            2. 初始化摄像头选择下拉框。
            3. 设置默认摄像头分辨率。
        """
        # 获取可用摄像头数量
        camera_nums = count_cameras()


        # 如果有可用摄像头
        if camera_nums > 0:
            logger.info(f"检测到 {camera_nums} 个摄像头")

            # 创建摄像头选项列表(0 到摄像头数量)
            camera_items = [str(i) for i in range(camera_nums + 1)]

            # 设置摄像头选择下拉框选项
            self.m_comboBox_select_camera.SetItems(camera_items)

            # 默认选择第一个摄像头
            self.m_comboBox_select_camera.SetSelection(0)

            self.camera_capture = get_camera(
                int(self.m_comboBox_select_camera.GetValue()))
            if self.camera_capture:
                # 获取 m_comboBox_select_camera 摄像头支持的分辨率列表(从最大到 720p)
                self.resolution_list = get_camera_supported_resolutions(
                    self.camera_capture)

                # 获取该摄像头支持的所有分辨率
                self.camera_supported_resolutions = get_camera_supported_resolutions(
                    self.camera_capture)
                logger.info(f"摄像头支持的分辨率列表: {self.camera_supported_resolutions}")

                # 初始化分辨率选择下拉框
                self.m_comboBox_select_camera_resolution.SetItems([
                    f"{resolution[0]}x{resolution[1]}"
                    for resolution in self.resolution_list
                ])


                if self.PREFERRED_RESOLUTION in self.camera_supported_resolutions:
                    index = self.camera_supported_resolutions.index(self.PREFERRED_RESOLUTION)
                else:
                    # 如果没有 1920x1440，选择最接近的分辨率
                    index = min(range(len(self.camera_supported_resolutions)),
                                key=lambda i: abs(self.camera_supported_resolutions[
                                    i][0] - self.PREFERRED_RESOLUTION[0]) +
                                abs(self.camera_supported_resolutions[i][1] -
                                    self.PREFERRED_RESOLUTION[1]))

                # 设置下拉框默认选择项
                self.m_comboBox_select_camera_resolution.SetSelection(index)
        else:
            self.camera_capture=None
            logger.error("本地未找到可用摄像头")

    def start_camera(self):
        """初始化摄像头并启动采集线程"""

        self._release_camera_resources()

        # 初始化摄像头
        if self.use_webcam:
            self.webcam_ip_address = self.m_web_camera_address.GetValue()
            if not self.webcam_ip_address:
                self._show_error("网络摄像头地址不正确")
                return

            logger.info(f"网络摄像头地址: {self.webcam_ip_address}")
            self.init_web_camera()
            if self.camera_capture:
                self.camera_resolution = get_camera_resolution(self.camera_capture)
            else:
                self._show_error("无法连接网络摄像头")
                self._release_camera_resources()
                return
        else:

            self.init_local_camera()

            if not self.camera_capture:
                self._show_error("无法初始化本地摄像头")
                self._release_camera_resources()
                print("------------")
                return

        # 启动采集线程
        try:
            
            self._prepare_display_area(debug=self.debug)
            self.is_camera_capture_running = True

            frame_interval_ms = 1000 / self.fps  # ✅ 推荐这样传参清晰
            self.capture_thread = threading.Thread(
                target=self.update_frame,
                args=(frame_interval_ms,self.update_frame_debug),
                daemon=True
            )
            self.capture_thread.start()
            logger.info("摄像头线程已启动")

        except Exception as e:
            logger.exception(f"启动摄像头时出错: {e}")
            self._show_error(str(e))
            self._release_camera_resources()


    def update_frame(self, target_fps=30,debug=False):
        """
        更新摄像头帧的线程方法。

        Args:
            target_fps (int): 目标帧率（每秒帧数），默认30。
        """
        # 计算每帧之间的时间间隔（秒）
        frame_interval_sec = 1.0 / target_fps
        
        last_processed_frame = None

        # 当摄像头正常打开且捕获线程运行标志为 True 时，持续循环
        while self.camera_capture.isOpened() and self.is_camera_capture_running:
            # 记录当前时间，用于计算处理一帧图像的耗时
            start_time = time.time()

            # 从摄像头读取一帧图像，ret 表示是否成功读取，frame 为读取的图像帧
            ret, frame = self.camera_capture.read()

            if ret:  # 如果成功读取到图像帧

                # 复制旋转后的图像帧，作为当前捕获的图像帧
                _frame = frame.copy()
                # 根据设置的旋转角度对图像进行旋转
                _frame = rotate_frame(_frame, self.image_rotation)

                # # 如果启用了曲面展平功能
                if self.is_surface_rectification_enabled:
                    # 对图像进行曲面展平处理
                    _frame = transform_document(_frame)
                # 如果启用了方框检测功能
                elif self.is_document_outline_detection_enabled:
                    # 检测图像中的轮廓，_contour 为检测到的轮廓，frame 为处理后的图像
                    _contour, _frame = detect_contour(_frame)
                    if _contour is not None:  # 如果检测到轮廓
                        # 在图像上绘制方框
                        _frame = draw_boxes_on_image(_frame, _contour)
                    else:
                        logger.debug("未检测到轮廓")
                # 减少不必要的 UI 更新
                if last_processed_frame is None or not np.array_equal(_frame, last_processed_frame):
                    
                    last_processed_frame = _frame
                    # 异步调用 update_bitmap 方法，确保在主线程中更新 UI
                    wx.CallAfter(self.update_bitmap, _frame)

            # 计算从开始读取帧到当前的处理耗时
            elapsed = time.time() - start_time
            if debug:
                logger.debug(f"处理一帧图像耗时: {elapsed:.4f} 秒")
                logger.debug(f"读取到的图像尺寸: {frame.shape}")
            # 计算需要休眠的时间，确保帧率稳定，若为负数则取 0
            sleep_time = max(0, frame_interval_sec - elapsed)
            # 线程休眠相应时间，维持固定帧率
            time.sleep(sleep_time)

    def update_bitmap(self, frame):
        """
        更新显示的位图（居中缩放版）。
        将 frame 等比缩放并居中绘制在与显示控件尺寸一致的画布上，然后显示。
        特点：
            图像等比缩放，无拉伸、不变形；
            居中显示，无论控件多大；
            不使用 wx.Image 转换，提高性能；
            背景为黑色，可改白色（用 np.full(..., 255, ...)）或自定义颜色。
        """
        if not hasattr(self, "m_bitmap_camera"):
            return

        # 获取控件大小
        camera_size = self.m_bitmap_camera.GetSize()
        camera_width = camera_size.GetWidth()
        camera_height = camera_size.GetHeight()

        # 原始图像尺寸
        h, w = frame.shape[:2]
        aspect_ratio = w / h

        # 计算缩放后的尺寸（保持宽高比）
        if camera_width / camera_height > aspect_ratio:
            # 控件的宽高比大于图像的宽高比，高度填满控件
            new_height = camera_height
            # 根据高度计算缩放后的宽度
            new_width = int(camera_height * aspect_ratio)
        else:
            # 控件的宽高比小于等于图像的宽高比，宽度填满控件
            new_width = camera_width
            # 根据宽度计算缩放后的高度
            new_height = int(camera_width / aspect_ratio)

        # 缩放图像
        resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        # 创建与控件一样大的背景画布（可改成白色或其他颜色）
        # canvas = np.zeros((camera_height, camera_width, 3), dtype=np.uint8) # 白色背景
        # canvas = np.full((camera_height, camera_width, 3), (200, 200, 200), dtype=np.uint8)  # 浅灰背景
        
        # 创建与控件一样大的背景画布（可改成白色或其他颜色），使用缓存
        if self.canvas_cache is None or self.canvas_cache.shape[:2] != (camera_height, camera_width):
            self.canvas_cache = np.full((camera_height, camera_width, 3), (200, 200, 200), dtype=np.uint8)  # 浅灰背景
        else:
            self.canvas_cache[:] = (200, 200, 200)  # 重置背景颜色

        # 计算居中位置
        x_offset = (camera_width - new_width) // 2
        y_offset = (camera_height - new_height) // 2

        # 将缩放后的图像粘贴到画布中心
        self.canvas_cache[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame

        # 转为 RGB（wx.Bitmap 需要 RGB 顺序）
        canvas_rgb = cv2.cvtColor(self.canvas_cache, cv2.COLOR_BGR2RGB)
        # 确保数组内存连续，满足 wx.Bitmap 的要求
        canvas_rgb = np.ascontiguousarray(canvas_rgb)

        # 创建 wx.Bitmap 并显示
        self.bitmap = wx.Bitmap.FromBuffer(camera_width, camera_height, canvas_rgb)
        self.m_bitmap_camera.SetBitmap(self.bitmap)
        # self.m_bitmap_camera.Refresh()
        # 获取包含摄像头图像的 sizer
        sizer = self.m_bitmap_camera.GetContainingSizer()
        # 刷新 sizer，确保显示最新的位图
        sizer.Layout()
        # 刷新整个对话框，确保所有组件都得到正确显示
        self.Refresh()

    def on_document_outline_detection(self, event):
        """
        处理方框检测的事件。
        此方法负责切换是否启用方框检测功能，并更新相关的 UI 组件。

        Args:
            event: 触发事件的事件对象
        """
        if self.is_document_outline_detection_enabled == False:
            # 如果当前未启用方框检测，则启用它并更新复选框状态
            self.m_checkBox_detect_squares.SetValue(True)
            self.is_document_outline_detection_enabled = True
            # 禁用曲面展平功能
            self.is_surface_rectification_enabled = False
            self.m_checkBox_rectify_surface.SetValue(False)
            
        else:
            # 如果当前已启用方框检测，则禁用它并更新复选框状态
            self.m_checkBox_detect_squares.SetValue(False)
            self.is_document_outline_detection_enabled = False
        logger.info(f"切换是否绘制方框: {self.is_document_outline_detection_enabled}")

    def on_rectify_surface(self, event):
        """
        处理曲面展平的事件。
        此方法负责切换是否启用曲面展平功能，并更新相关的 UI 组件。

        Args:
            event: 触发事件的事件对象
        """
        if self.is_surface_rectification_enabled == False:
            # 如果当前未启用曲面展平，则启用它并更新复选框状态
            self.m_checkBox_rectify_surface.SetValue(True)
            self.is_surface_rectification_enabled = True
            # 禁用方框检测功能
            self.m_checkBox_detect_squares.SetValue(False)
            self.is_document_outline_detection_enabled = False
        else:
            # 如果当前已启用曲面展平，则禁用它并更新复选框状态
            self.m_checkBox_rectify_surface.SetValue(False)
            self.is_surface_rectification_enabled = False
        logger.info(f"切换是否曲面找平: {self.is_surface_rectification_enabled}")

    def on_take_photo(self, event):
        """
        此方法负责拍照并保存摄像头获得的原始图像。

        Args:
            event: 触发事件的事件对象，通常由用户点击拍照按钮等操作触发。
        """

        if self.current_captured_frame is not None:
            try:
                # 构建保存文件的完整路径
                if self.m_checkBox_saveByGroup.IsChecked():
                    logger.info(f"保存文件到组: {self.m_TextCtrl_GroupName.GetValue()}")
                    path = get_save_path(group_name=self.m_TextCtrl_GroupName.GetValue())
                else:
                    path = get_save_path()

                # 保存图像
                frame = self.current_captured_frame
                save_image(frame, path)
                self.m_statusBar.SetStatusText(f"已保存图片: {path}")

                if self.m_checkBox_saveByGroup.IsChecked():
                    wx.CallAfter(self.m_thumbnailgallery.add_image, path,group_name=self.m_TextCtrl_GroupName.GetValue(),)
                else:
                    wx.CallAfter(self.m_thumbnailgallery.add_image, path)
            except Exception as e:
                logger.error(f"on_take_photo 保存图像时出错: {e}")
                self._show_error(f"保存图像失败: {e}")
                self.m_statusBar.SetStatusText(f"保存图片失败: {e}")
        else:
            logger.error("on_take_photo 没有捕获到图像")
            return


    def on_take_document(self, event):
        """
        此方法负责拍照并保存曲面找平的图像。

        Args:
            event: 触发事件的事件对象
        """
        if self.current_captured_frame is not None:
            try:
                # 构建保存文件的完整路径
                if self.m_checkBox_saveByGroup.IsChecked():
                    logger.info(f"保存文件到组: {self.m_TextCtrl_GroupName.GetValue()}")
                    path = get_save_path(group_name=self.m_TextCtrl_GroupName.GetValue())
                else:
                    path = get_save_path()
                # 保存图像
                # 对图像进行曲面展平处理
                logger.debug("保存曲面展平处理后的图像")
                frame = transform_document(self.current_captured_frame)

                save_image(frame, path)
                self.m_statusBar.SetStatusText(f"已保存图片: {path}")

                if self.m_checkBox_saveByGroup.IsChecked():
                    wx.CallAfter(self.m_thumbnailgallery.add_image, path,group_name=self.m_TextCtrl_GroupName.GetValue(),)
                else:
                    wx.CallAfter(self.m_thumbnailgallery.add_image, path)
            except Exception as e:
                logger.error(f"on_take_document 保存图像时出错: {e}")
                self._show_error(f"保存图像失败: {e}")
                self.m_statusBar.SetStatusText(f"保存图片失败: {e}")
        else:
            logger.error("on_take_document 没有捕获到图像")
            return
    def on_take_pdf_doc(self, event):
        """
        此方法负责将当前图像曲面找平后保存为pdf文件。
        Args:
            event: 触发事件的事件对象
        """
        if self.current_captured_frame is not None:
            try:
                # 构建保存文件的完整路径
                if self.m_checkBox_saveByGroup.IsChecked():
                    logger.info(f"保存文件到组: {self.m_TextCtrl_GroupName.GetValue()}")
                    path = get_save_path(suffix="pdf",group_name=self.m_TextCtrl_GroupName.GetValue())
                else:
                    path = get_save_path("pdf")

                # 对图像进行曲面展平处理
                logger.debug("保存曲面展平处理后的图像为 PDF 文件")
                frame = transform_document(self.current_captured_frame)
                save_pdf(frame, path)
                self.m_statusBar.SetStatusText(f"保存PDF文件成功：{path}")
            except Exception as e:
                logger.error(f"on_take_pdf_doc 保存PDF文件时出错: {e}")
                self._show_error(f"保存PDF文件失败: {e}")
                self.m_statusBar.SetStatusText("保存PDF文件失败: {e}")
        else:
            logger.error("on_take_pdf_doc 没有捕获到图像")
            return
    def on_take_mutip_pdf_doc(self, event):
        """
        此方法负责将预览栏中所有图像曲面找平后保存为pdf文件。
        Args:
            event: 触发事件的事件对象
        """
        try:
            # 构建保存文件的完整路径
            if self.m_checkBox_saveByGroup.IsChecked():
                logger.info(f"保存文件到组: {self.m_TextCtrl_GroupName.GetValue()}")
                path = get_save_path(suffix="pdf",prefix="合并", group_name=self.m_TextCtrl_GroupName.GetValue())
            else:
                path = get_save_path(suffix="pdf",prefix="合并")

            images_path=self.m_thumbnailgallery.get_images()
            save_multip_pdf(images_path,path)
            self.m_statusBar.SetStatusText(f"合并PDF文件成功：{path}")
        except Exception as e:
            logger.error(f"on_take_mutip_pdf_doc 批量合并保存PDF文件时出错: {e}")
            self._show_error('批量合并保存PDF文件时出错!')
            self.m_statusBar.SetStatusText("合并PDF文件失败: {e}")  
    def on_merge_photos(self, event):
        """
        此方法负责将预览栏中所有图像合并为一个长图片文件。
        Args:
            event: 触发事件的事件对象
        """
        try:
            # 构建保存文件的完整路径
            if self.m_checkBox_saveByGroup.IsChecked():
                logger.info(f"保存文件到组: {self.m_TextCtrl_GroupName.GetValue()}")
                path = get_save_path(suffix="jpg",prefix="合并",group_name=self.m_TextCtrl_GroupName.GetValue())
            else:
                path = get_save_path(suffix="jpg",prefix="合并")


            images_path=self.m_thumbnailgallery.get_images()
            padding=self.config.get('SCANNER', 'merge_image_interval')
            merge_images(images_path,path,padding=padding)
            self.m_statusBar.SetStatusText(f"合并图片成功：{path}")
        except Exception as e:
            logger.error(f"on_merge_photos 合并图片时出错: {e}")
            self._show_error('合并图片时出错!')
            self.m_statusBar.SetStatusText("合并图片失败: {e}")

    def on_take_card(self, event):
        """
        拍照并保存检测到的卡片图像
        """
        if self.current_captured_frame is not None:
            try:

                frame = self.current_captured_frame
                outimg, corner_points_list = self.card_net.detect(frame)

                if not corner_points_list:
                    logger.warning("未检测到任何卡片")
                    wx.CallAfter(wx.MessageBox, "未检测到任何卡片", "提示", wx.OK | wx.ICON_INFORMATION)
                    return

                logger.info(f"检测到 {len(corner_points_list)} 个卡片")
                crops = []

                for i, corner_points in enumerate(corner_points_list):
                    points = np.array(corner_points)
                    x, y, w, h = cv2.boundingRect(points)
                    crops.append((x, y, w, h))

                if crops:
                    x, y, w, h = crops[0]
                    cropped = frame[y:y + h, x:x + w]
                    # cropped = cv2.resize(cropped, (800, 500)) # 保存为缩略图

                    if self.m_checkBox_saveByGroup.IsChecked():
                        logger.info(f"保存文件到组: {self.m_TextCtrl_GroupName.GetValue()}")
                        path = get_save_path(suffix="jpg", prefix="卡片", group_name=self.m_TextCtrl_GroupName.GetValue())
                    else:
                        path = get_save_path(suffix="jpg", prefix="卡片")

                    save_image(cropped, path)
                    self.m_statusBar.SetStatusText(f"保存卡片图片成功：{path}")
                    if self.m_checkBox_saveByGroup.IsChecked():
                        wx.CallAfter(self.m_thumbnailgallery.add_image, path, group_name=self.m_TextCtrl_GroupName.GetValue(), )
                    else:
                        wx.CallAfter(self.m_thumbnailgallery.add_image, path)
            except Exception as e:
                logger.error(f"on_take_card 保存卡片图像时出错: {e}")
                self._show_error(f"保存卡片图像失败: {e}")
                self.m_statusBar.SetStatusText("保存卡片图片失败: {e}")
        else:
            logger.error("on_take_card 没有捕获到图像")
            return


    def on_right_rotation(self, event):
        """
        处理左旋转的事件。
        此方法负责将 self.image_rotation 的值增加 90 度，当旋转累计达到一周（360 度）时，将其归 0。
        旋转角度的更新会记录日志，方便后续调试与追踪。

        Args:
            event: 触发事件的事件对象
        """
        # 将旋转角度增加 90 度，并通过取模运算确保角度在 0 到 359 度之间
        self.image_rotation = (self.image_rotation + 90) % 360
        # 记录旋转后的角度信息
        logger.debug(f"执行左旋转操作，当前累计旋转角度: {self.image_rotation} 度")

    def on_left_rotation(self, event):
        """
        处理右旋转的事件。
        此方法负责将 self.image_rotation 的值减少 90 度，利用取模运算保证角度在 0 到 359 度的范围。
        每次旋转操作后，会记录日志，方便后续调试和追踪。

        Args:
            event: 触发事件的事件对象
        """
        # 将旋转角度减少 90 度，并通过取模运算确保角度在 0 到 359 度之间
        self.image_rotation = (self.image_rotation - 90) % 360
        # 记录旋转后的角度信息
        logger.debug(f"执行右旋转操作，当前累计旋转角度: {self.image_rotation} 度")
    def on_checkBox_saveByGroup(self, event):
        """
        处理分组保存复选框的事件。
        此方法负责根据复选框的状态更新界面的显示，并记录日志。
        Args:
            event: 触发事件的事件对象
        """
        # 检查复选框的状态
        if event.IsChecked():
            # 如果复选框被选中，则分组名称输入框可以输入文本
            self.m_TextCtrl_GroupName.Enable(True)
            logger.debug("启用分组保存功能")
        else:
            # 如果复选框未被选中，则分组名称输入框不可输入文本
            self.m_TextCtrl_GroupName.Enable(False)
            logger.debug("禁用分组保存功能")
    def _prepare_display_area(self,debug=True):
        """根据布局设置摄像头显示区域尺寸"""
        # 获取包含摄像头图像的 sizer
        sizer = self.m_bitmap_camera.GetContainingSizer()
        if sizer:
            # 如果 sizer 存在，获取其尺寸
            size = sizer.GetSize()
            if debug:
                logger.debug(f"摄像头图像的 size: {size}")
            # 设置摄像头图像控件的尺寸为 sizer 的尺寸
            self.m_bitmap_camera.SetSize(size)
            # 将摄像头显示区域的尺寸设置为与 sizer 尺寸一致
            self.camera_resolution = size  # 以 sizer 尺寸为准
    def _release_camera_resources(self):
        """释放旧摄像头资源与线程"""
        try:
            if hasattr(self, "capture_thread") and self.capture_thread and self.capture_thread.is_alive():
                self.is_camera_capture_running = False
                self.capture_thread.join(timeout=1)
            if hasattr(self, "camera_capture") and self.camera_capture is not None:
                self.camera_capture.release()
        except Exception as e:
            logger.error(f"释放摄像头失败: {e}")
            # 检查是否使用网络摄像头且摄像头可读取
            if self.use_webcam and self.webcam_url:
                # 保存网络摄像头 IP 地址到配置文件
                self.config.set('CAMERA', 'ip_address', self.webcam_url)
                save_config(self.config)
                logger.info(f"已保存网络摄像头 IP 地址: {self.webcam_url}")
        except Exception as e:
            logger.error(f"释放摄像头异常: {e}")
            self._show_error(f"释放摄像头资源异常: {e}")

    def _show_error(self, message, title="错误"):
        logger.error(message)
        wx.CallAfter(wx.MessageBox, message, title, wx.OK | wx.ICON_ERROR)

    def on_close(self, event):
        """
        程序退出时的处理方法。
        此方法负责停止所有正在运行的进程，保存配置，
        销毁系统托盘图标和主窗口，最后退出应用程序。

        Args:
            event: 触发退出的事件对象（未使用）
        """
        logger.debug("开始执行退出操作")

        # 停止线程
        logger.debug("正在停止摄像头线程")

        self._release_camera_resources()


        logger.debug("摄像头线程已停止")

        # 销毁主窗口
        logger.debug("正在销毁主窗口")
        self.Destroy()

        # 使用 wx.CallAfter 确保在主事件循环中退出应用
        logger.debug("准备退出应用程序")
        wx.CallAfter(wx.GetApp().ExitMainLoop)

    def on_setting(self, event):
        """
        处理打开设置窗口的事件。

        Args:
            event: 触发事件的事件对象
        """
        # 打开设置窗口
        config_frame = ConfigFrame(parent=self)
        config_frame.Show()
        # 继续处理其他事件
        event.Skip()


if __name__ == '__main__':
    # 创建 wxPython 应用程序对象
    app = wx.App()
    # 创建主应用程序框架对象
    frame = Main_Frame()
    # 显示主窗口
    frame.Show()
    # 进入主事件循环
    app.MainLoop()
