import wx
import os
import sys
import threading
import time
from pathlib import Path
import cv2
from Document_Scanner_UI import Main_Ui_Frame
from cammer_utils import get_camera_max_resolution, count_cameras, set_camera_resolution, detect_and_draw_boxes, get_camera_resolution_list
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

        camera_nums = count_cameras()
        if camera_nums > 0:
            # 根据指定摄像头的分辨率列表，返回一个分辨率列表：从最大分辨率开始，直至720p。
            self.resolution_list = get_camera_resolution_list(0)
            # 初始化摄像头选择下拉框
            self.m_comboBox_select_camera.SetItems(
                [str(i) for i in range(camera_nums + 1)])
            self.m_comboBox_select_camera.SetSelection(0)

            self.camera_index = int(
                self.m_comboBox_select_camera.GetValue())  #选择的摄像头索引
            self.camera_resolution_list = get_camera_resolution_list(
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
        while self.capture.isOpened() and self.capture_running:
            ret, frame = self.capture.read()
            self.frame = frame
            if ret:
                if self.enable_square_detection:
                    frame = detect_and_draw_boxes(frame)
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
            
            self.m_bitmap_camera.SetBitmap(self.bitmap)
            self.Refresh()
    def on_detect_squares(self, event):
        if self.enable_square_detection == False:
            self.m_checkBox_detect_squares.SetValue(True)
            self.enable_square_detection = True
        else:
            self.m_checkBox_detect_squares.SetValue(False)
            self.enable_square_detection = False
        logger.info(f"切换是否绘制方框: {self.enable_square_detection}")

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
