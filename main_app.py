import wx
import os
import sys
import threading
import time
from pathlib import Path
import cv2
from Document_Scanner_UI import Main_Ui_Frame
from cammer_utils import get_camera_max_resolution, rotate_frame,count_cameras, set_camera_resolution, detect_contour, get_camera_supported_resolutions,draw_boxes_on_image,transform_document
from loguru import logger

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))


class Main_Frame(Main_Ui_Frame):

    def __init__(self):
        super().__init__(parent=None)
        self.camera_index = -1
        self.camera_resolution = None
        self.fps = 30
        self.frame = None
        self.capture_running = False  # 添加一个标志位来控制线程的运行状态
        self.enable_square_detection = False  # 添加一个标志位来控制是否启用方框检测
        self.enable_rectify_surface =False # 添加一个标志位来控制是否启用曲面展平
        self.m_checkBox_rectify_surface.SetValue(self.enable_rectify_surface)
        self.frame_rotation = 0  # 初始旋转角度为0


        camera_nums = count_cameras()
        if camera_nums > 0:
            # 根据指定摄像头的分辨率列表，返回一个分辨率列表：从最大分辨率开始，直至720p。
            self.resolution_list = get_camera_supported_resolutions(0)
            # 初始化摄像头选择下拉框
            self.m_comboBox_select_camera.SetItems(
                [str(i) for i in range(camera_nums + 1)])
            self.m_comboBox_select_camera.SetSelection(0)

            self.camera_index = int(
                self.m_comboBox_select_camera.GetValue())  #选择的摄像头索引
            self.camera_resolution_list = get_camera_supported_resolutions(
                self.camera_index)  # 获取摄像头支持的分辨率列表
            logger.info(
                f"摄像头-- {self.camera_index} 支持的分辨率列表: {self.camera_resolution_list}"
            )
            # 初始化摄像头分辨率选择下拉框
            self.m_comboBox_select_camera_resolution.SetItems([
                f"{resolution[0]}x{resolution[1]}"
                for resolution in self.resolution_list
            ])

            # 初始化摄像头分辨率选择下拉框默认值
            # 筛选出最接近1920*1020的项的索引
            preferred_res = (1920, 1440)
            if preferred_res in self.camera_resolution_list:
                index = self.camera_resolution_list.index(preferred_res)
            else:
                # 选择最接近目标分辨率的分辨率
                index = min(
                    range(len(self.camera_resolution_list)),
                    key=lambda i: abs(self.camera_resolution_list[i][0] -
                                      preferred_res[0]) +
                    abs(self.camera_resolution_list[i][1] - preferred_res[1]))

            self.m_comboBox_select_camera_resolution.SetSelection(index)

            self.start_camera()

    def start_camera(self):
        """
        初始化摄像头并启动摄像头线程。

        此方法负责根据用户选择的摄像头和分辨率进行初始化，并启动一个独立的线程来更新摄像头帧。

        Raises:
            RuntimeError: 如果无法打开摄像头，则抛出运行时错误。
        """
        # 初始化摄像头
        self.camera_index = int(self.m_comboBox_select_camera.GetValue())
        self.camera_resolution = self.camera_resolution_list[
            self.m_comboBox_select_camera_resolution.GetSelection()]
        width = self.camera_resolution[0]
        height = self.camera_resolution[1]

        update_time = 1000 // self.fps  # 计算定时器的时间间隔（毫秒）

        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            # 设置摄像头分辨率
            set_camera_resolution(self.capture, width, height)
            logger.info(
                f"设置后摄像头-- {self.camera_index} ,目标分辨率: {self.camera_resolution}"
            )
            if not self.capture.isOpened():
                raise RuntimeError(f"无法打开摄像头 {self.camera_index}")

            self.m_bitmap_camera.SetSize(self.camera_resolution)

            self.capture_running = True
            # 启动摄像头线程
            self.capture_thread = threading.Thread(target=self.update_frame,
                                                   args=(update_time, ),
                                                   daemon=True)
            self.capture_thread.start()
            logger.info("摄像头线程已启动")

        except Exception as e:
            logger.exception(f"启动摄像头时出错: {e}")
            wx.CallAfter(wx.MessageBox, str(e), "错误", wx.OK | wx.ICON_ERROR)

    def update_frame(self, update_time):
        """
        更新摄像头帧的线程方法。

        此方法在一个独立的线程中运行，持续从摄像头读取帧并进行处理。
        如果启用了方框检测，则在帧上绘制方框。然后将帧转换为wx.Bitmap格式，
        并调用update_bitmap方法更新显示的位图。

        Args:
            update_time (int): 帧更新的时间间隔（毫秒）。
        """
        while self.capture.isOpened() and self.capture_running:
            ret, frame = self.capture.read()

            if ret:
                # 根据self.frame_rotation 旋转图像
                frame=rotate_frame(frame, self.frame_rotation)
                self.frame = frame.copy()# 保存原始帧

                # 如果启用了曲面展平，则在帧上绘制曲面展平后的图像
                if self.enable_rectify_surface:
                    frame = transform_document(frame)
                else:
                    # 如果启用了方框检测，则在帧上绘制方框
                    if self.enable_square_detection:
                        _contour, frame = detect_contour(frame)
                        # 绘制边界框
                        if _contour is not None:
                            frame = draw_boxes_on_image(frame, _contour)

                # 将图像从BGR转换为RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = frame.shape[:2]
                # 创建wx.Image对象
                image = wx.Image(w, h)
                # 设置图像数据
                image.SetData(frame.tobytes())
                # 转换为wx.Bitmap
                self.bitmap = wx.Bitmap(image)
                wx.CallAfter(self.update_bitmap)
            time.sleep(update_time / 1000.0)  # 控制帧率

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
            self.Refresh()
    def on_detect_squares(self, event):
        """
        处理方框检测的事件。

        此方法负责切换是否启用方框检测功能，并更新相关的UI组件。

        Args:
            event: 触发事件的事件对象
        """
        if self.enable_square_detection == False:
            # 如果当前未启用方框检测，则启用它并更新复选框状态
            self.m_checkBox_detect_squares.SetValue(True)
            self.enable_square_detection = True
        else:
            # 如果当前已启用方框检测，则禁用它并更新复选框状态
            self.m_checkBox_detect_squares.SetValue(False)
            self.enable_square_detection = False
        logger.info(f"切换是否绘制方框: {self.enable_square_detection}")
    def on_rectify_surface(self, event):
        """
        处理曲面展平的事件。

        此方法负责切换是否启用曲面展平功能，并更新相关的UI组件。

        Args:
            event: 触发事件的事件对象
        """
        if self.enable_rectify_surface == False:
            # 如果当前未启用曲面展平，则启用它并更新复选框状态
            self.m_checkBox_rectify_surface.SetValue(True)
            self.enable_rectify_surface = True
        else:
            # 如果当前已启用曲面展平，则禁用它并更新复选框状态
            self.m_checkBox_rectify_surface.SetValue(False)
            self.enable_rectify_surface = False
        logger.info(f"切换是否曲面找平: {self.enable_rectify_surface}")

    def on_take_photo(self, event):
        """
        此方法负责拍照并保存摄像头获得的原始图像。
        Args:
            event: 触发事件的事件对象
        """

        if self.frame is not None:

            cv2.imwrite("temp_no_surface.jpg", self.frame)
        else:
            logger.error("没有捕获到图像")
            return
    def on_take_document(self, event):
        """
        此方法负责拍照并保存曲面找平的图像。
        Args:
            event: 触发事件的事件对象
        """
        if self.frame is not None:

            _frame = transform_document(self.frame)
            cv2.imwrite("temp_surface.jpg", _frame)
        else:
            logger.error("没有捕获到图像")
            return

    def on_right_rotation(self, event):
        """
        处理左旋转的事件。
        此方法负责将 self.frame_rotation 的值增加 90 度，当旋转累计达到一周（360 度）时，将其归 0。
        旋转角度的更新会记录日志，方便后续调试与追踪。

        Args:
            event: 触发事件的事件对象
        """
        # 将旋转角度增加 90 度，并通过取模运算确保角度在 0 到 359 度之间
        self.frame_rotation = (self.frame_rotation + 90) % 360
        # 记录旋转后的角度信息
        logger.debug(f"执行左旋转操作，当前累计旋转角度: {self.frame_rotation} 度")

    def on_left_rotation(self, event):
        """
        处理右旋转的事件。
        此方法负责将 self.frame_rotation 的值减少 90 度，利用取模运算保证角度在 0 到 359 度的范围。
        每次旋转操作后，会记录日志，方便后续调试和追踪。

        Args:
            event: 触发事件的事件对象
        """
        # 将旋转角度减少 90 度，并通过取模运算确保角度在 0 到 359 度之间
        self.frame_rotation = (self.frame_rotation - 90) % 360
        # 记录旋转后的角度信息
        logger.debug(f"执行右旋转操作，当前累计旋转角度: {self.frame_rotation} 度")
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
        if hasattr(self, "capture") and self.capture.isOpened():
            self.capture_running = False
            self.capture.release()  # 释放摄像头资源
            self.capture_thread.join()  # 等待线程结束
        logger.debug("摄像头线程已停止")

        # 销毁主窗口
        logger.debug("正在销毁主窗口")
        self.Destroy()

        # 使用 wx.CallAfter 确保在主事件循环中退出应用
        logger.debug("准备退出应用程序")
        wx.CallAfter(wx.GetApp().ExitMainLoop)


if __name__ == '__main__':
    app = wx.App()

    frame = Main_Frame()

    frame.Show()

    app.MainLoop()
