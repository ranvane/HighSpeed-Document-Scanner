import wx
import os
import threading
import time
import cv2
# 从自定义模块中导入主用户界面框架类
from Document_Scanner_UI import Main_Ui_Frame
# 从自定义摄像头工具模块中导入使用的函数
from cammer_utils import get_camera_resolution, get_camera, rotate_frame, count_cameras, detect_contour, get_camera_supported_resolutions, draw_boxes_on_image, transform_document
from loguru import logger
from app_config import get_config, save_config
# 从自定义配置界面模块中导入配置窗口类
from config_ui import ConfigFrame  # 这是一个自定义的配置窗口类
from datetime import datetime
from utils import save_image,save_pdf,save_multip_pdf,get_save_path

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
            # self.GetSizer().Layout()
            # self.Refresh()
            # self.Update()
            # self.Layout()
            # self.Refresh()

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
            logger.error("未找到可用摄像头")

    def start_camera(self):
        """
        初始化摄像头并启动摄像头线程。
        此方法负责根据用户选择的摄像头和分辨率进行初始化，并启动一个独立的线程来更新摄像头帧。

        Raises:
            RuntimeError: 如果无法打开摄像头，则抛出运行时错误。
        """
        frame_interval_ms = 1000 // self.fps
        try:
            if hasattr(self, "camera_capture") and self.camera_capture is not None:
                logger.debug("新连接前释放摄像头资源")
                self.is_camera_capture_running = False
                try:
                    self.camera_capture.release()
                    if hasattr(self, "capture_thread") and self.capture_thread.is_alive():
                        logger.debug("新连接前释放摄像头摄像头线程")
                        self.capture_thread.join(timeout=1)
                except Exception as e:
                    logger.warning(f"新连接前释放摄像头摄像头线程: {e}")
                    wx.CallAfter(wx.MessageBox, f"新连接前释放摄像头摄像头线程: {e}", "警告", wx.OK | wx.ICON_WARNING)
        except Exception as e:
            logger.error(f"新连接前释放摄像头资源: {e}")
            wx.CallAfter(wx.MessageBox, f"新连接前释放摄像头资源: {e}", "错误", wx.OK | wx.ICON_ERROR)
            return

        if self.use_webcam:
            self.webcam_ip_address = self.m_web_camera_address.GetValue()
            if not self.webcam_ip_address:
                logger.error("网络摄像头地址不正确")
                wx.CallAfter(wx.MessageBox, "网络摄像头地址不正确", "错误", wx.OK | wx.ICON_ERROR)
                return
            logger.info(f"网络摄像头地址: {self.webcam_ip_address}")
            self.init_web_camera()
            if self.camera_capture:
                self.camera_resolution = get_camera_resolution(self.camera_capture)
            else:
                wx.CallAfter(wx.MessageBox, "无法连接网络摄像头", "错误", wx.OK | wx.ICON_ERROR)
                return
        else:
            self.init_local_camera()
            if not self.camera_capture:
                wx.CallAfter(wx.MessageBox, "无法初始化本地摄像头", "错误", wx.OK | wx.ICON_ERROR)
                return

        if self.camera_capture:
            try:
                # 获取 m_bitmap_camera 所在 sizer 的尺寸
                sizer = self.m_bitmap_camera.GetContainingSizer()
                if sizer:
                    sizer_size = sizer.GetSize()
                    self.m_bitmap_camera.SetSize(sizer_size)
                    self.camera_resolution = sizer_size  # 以 sizer 尺寸作为显示分辨率

                self.m_bitmap_camera.SetSize(self.camera_resolution)
                self.is_camera_capture_running = True
                self.capture_thread = threading.Thread(
                    target=self.update_frame,
                    args=(frame_interval_ms, ),
                    daemon=True)
                self.capture_thread.start()
                logger.info("摄像头线程已启动")
            except Exception as e:
                logger.exception(f"启动摄像头时出错: {e}")
                wx.CallAfter(wx.MessageBox, str(e), "错误", wx.OK | wx.ICON_ERROR)
        else:
            logger.error("无法打开摄像头")
            wx.CallAfter(wx.MessageBox, "没有找到摄像头", "没有找到摄像头", wx.OK | wx.ICON_ERROR)
    def update_frame(self, frame_interval_ms):
        """
        更新摄像头帧的线程方法。
        此方法在一个独立的线程中运行，持续从摄像头读取帧并进行处理。
        如果启用了方框检测，则在帧上绘制方框。然后将帧转换为 wx.Bitmap 格式，
        并调用 update_bitmap 方法更新显示的位图。

        Args:
            frame_interval_ms (int): 帧更新的时间间隔（毫秒）。
        """
        while self.camera_capture.isOpened() and self.is_camera_capture_running:
            # 从摄像头读取一帧图像
            ret, frame = self.camera_capture.read()

            if ret:
                # 根据 self.image_rotation 旋转图像
                frame = rotate_frame(frame, self.image_rotation)
                # 保存原始帧
                self.current_captured_frame = frame.copy()

                # 如果启用了曲面展平，则在帧上绘制曲面展平后的图像
                if self.is_surface_rectification_enabled:
                    frame = transform_document(frame)
                else:
                    # 如果启用了文档检测，则在帧上绘制边框
                    if self.is_document_outline_detection_enabled:
                        _contour, frame = detect_contour(frame)
                        # 绘制边界框
                        if _contour is not None:
                            frame = draw_boxes_on_image(frame, _contour)

                # 将图像从 BGR 转换为 RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 获取图像的高度和宽度
                h, w = frame.shape[:2]
                # 创建 wx.Image 对象
                image = wx.Image(w, h)
                # 设置图像数据
                image.SetData(frame.tobytes())
                # 转换为 wx.Bitmap
                self.bitmap = wx.Bitmap(image)
                # 在主线程中调用 update_bitmap 方法
                wx.CallAfter(self.update_bitmap)
            # 控制帧率
            time.sleep(frame_interval_ms / 1000.0)

    def update_bitmap(self):
        """
        更新显示的位图。
        此方法负责将捕获的图像调整大小以适应显示窗口，并更新显示的位图。
        如果捕获的图像存在，则获取显示窗口的大小，并根据图像的宽高比调整图像大小，
        以适应显示窗口。然后将调整后的图像设置为显示窗口的位图，并刷新窗口以显示新的图像。
        """
        if hasattr(self, "bitmap"):
            # 获取 m_bitmap_camera 的大小
            camera_size = self.m_bitmap_camera.GetSize()
            camera_width = camera_size.GetWidth()
            camera_height = camera_size.GetHeight()

            # 获取 bitmap 的原始大小
            image = self.bitmap.ConvertToImage()
            bitmap_width = image.GetWidth()
            bitmap_height = image.GetHeight()

            # 计算调整后的大小，保持比例
            aspect_ratio = bitmap_width / bitmap_height
            if camera_width / camera_height > aspect_ratio:
                new_height = camera_height
                new_width = int(camera_height * aspect_ratio)
            else:
                new_width = camera_width
                new_height = int(camera_width / aspect_ratio)

            # 调整 bitmap 的大小以适应 m_bitmap_camera
            image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
            self.bitmap = wx.Bitmap(image)

            # 设置调整后的 bitmap 到 m_bitmap_camera
            self.m_bitmap_camera.SetBitmap(self.bitmap)
            # 刷新窗口
            self.Refresh()

    def on_detect_squares(self, event):
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
        else:
            # 如果当前已启用曲面展平，则禁用它并更新复选框状态
            self.m_checkBox_rectify_surface.SetValue(False)
            self.is_surface_rectification_enabled = False
        logger.info(f"切换是否曲面找平: {self.is_surface_rectification_enabled}")

    def on_take_photo(self, event):
        """
        此方法负责拍照并保存摄像头获得的原始图像。

        Args:
            event: 触发事件的事件对象
        """
        if self.current_captured_frame is not None:
            # 构建保存文件的完整路径
            path = path = get_save_path()
            # 保存图像
            frame = self.current_captured_frame
            save_image(frame, path)

            self.m_thumbnailgallery.add_image(path)
        else:
            logger.error("没有捕获到图像")
            return

    def on_take_document(self, event):
        """
        此方法负责拍照并保存曲面找平的图像。

        Args:
            event: 触发事件的事件对象
        """
        if self.current_captured_frame is not None:
            # 构建保存文件的完整路径
            path = path = get_save_path()
            # 保存图像
            # 对图像进行曲面展平处理
            logger.debug("保存曲面展平处理后的图像")
            frame = transform_document(self.current_captured_frame)

            save_image(frame, path)

        else:
            logger.error("没有捕获到图像")
            return
    def on_take_pdf_doc(self, event):
        """
        此方法负责将当前图像曲面找平后保存为pdf文件。
        Args:
            event: 触发事件的事件对象
        """
        if self.current_captured_frame is not None:
            # 构建保存文件的完整路径
            path = get_save_path("pdf")

            # 对图像进行曲面展平处理
            logger.debug("保存曲面展平处理后的图像为 PDF 文件")
            frame = transform_document(self.current_captured_frame)
            save_pdf([frame], path)

        else:
            logger.error("没有捕获到图像")
            return
    def on_take_mutip_pdf_doc(self, event):
        """
        此方法负责将预览栏中所有图像曲面找平后保存为pdf文件。
        Args:
            event: 触发事件的事件对象
        """
        path = get_save_path("pdf")
        images_path=self.m_thumbnailgallery.get_images()
        save_multip_pdf(images_path,path)

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

        if hasattr(self, "capture"
                   ) and self.camera_capture is not None and self.camera_capture.isOpened():
            # 停止摄像头捕获线程
            self.is_camera_capture_running = False
            # 释放摄像头资源
            self.camera_capture.release()
            # 等待线程结束
            self.capture_thread.join()

            # 检查是否使用网络摄像头且摄像头可读取
            if self.use_webcam and self.webcam_url:
                # 保存网络摄像头 IP 地址到配置文件
                self.config.set('CAMERA', 'ip_address', self.webcam_url)
                save_config(self.config)
                logger.info(f"已保存网络摄像头 IP 地址: {self.webcam_url}")
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
