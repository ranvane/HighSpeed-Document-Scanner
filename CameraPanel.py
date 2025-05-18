import wx
import cv2
from cammer_utils import get_camera_max_resolution, set_camera_resolution,detect_and_draw_boxes

class CameraPanel(wx.Panel):
    def __init__(self, parent, desired_width=1280, desired_height=720, camera_index=0, fps=30):
        """
        初始化 CameraPanel 对象

        参数:
            parent: 父窗口
            desired_width: 期望的摄像头分辨率宽度 (默认值 1280)
            desired_height: 期望的摄像头分辨率高度 (默认值 720)
            camera_index: 摄像头索引 (默认值 0)
            fps: 每秒帧数 (默认值 30)
        """
        super().__init__(parent)
        self.camera_index = camera_index
        self.fps = fps

        # 获取摄像头最大分辨率
        max_width, max_height = get_camera_max_resolution(camera_index)

        # 限制目标分辨率不超过最大值
        width = min(desired_width, max_width)
        height = min(desired_height, max_height)

        # 设置摄像头分辨率
        set_camera_resolution(width, height, camera_index)

        # 打开摄像头
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            wx.MessageBox(f"无法打开摄像头 {camera_index}", "错误", wx.OK | wx.ICON_ERROR)
            return
        else:
            print(f"摄像头 {camera_index} 已打开")

        # 启动定时器刷新图像
        self.m_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_next_frame, self.m_timer)  # 当定时器触发时，将调用 self.on_next_frame 方法
        self.Bind(wx.EVT_PAINT, self.on_paint)  # 绘制事件 wx.EVT_PAINT 绑定到 self.on_paint 方法
        update_time = 1000 // fps  # 计算定时器的时间间隔（毫秒）
        self.m_timer.Start(update_time)  # 设置定时器的时间间隔

        self.bitmap = None

    def on_next_frame(self, event):
        """
        定时器事件处理函数，从摄像头读取下一帧并刷新面板
        """
        # 从摄像头读取下一帧
        ret, frame = self.capture.read()
        if ret:
            # frame=detect_and_draw_boxes(frame)
            # 将图像从BGR转换为RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]
            # 创建wx.Image对象
            image = wx.Image(w, h)
            # 设置图像数据
            image.SetData(frame.tobytes())
            # 转换为wx.Bitmap
            self.bitmap = wx.Bitmap(image)
            self.bitmap.SaveFile("test.png", wx.BITMAP_TYPE_PNG)
            # 刷新面板
            self.Refresh()
            self.Update()  # 强制立即重绘

    def on_paint(self, event):
        """
        绘制事件处理函数，在面板上绘制图像
        """
        # 如果有图像数据，绘制图像
        if self.bitmap:
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self.bitmap, 0, 0)

    def stop(self):
        """
        停止定时器并释放摄像头资源
        """
        # 停止定时器并释放摄像头资源
        if hasattr(self, 'timer'):
            self.m_timer.Stop()
        if hasattr(self, 'capture') and self.capture.isOpened():
            self.capture.release()