
import wx
from CameraPanel import CameraPanel
from cammer_utils import count_cameras

class CameraFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="多摄像头选择", size=(800, 600))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 下拉框：摄像头选择
        self.camera_choice = wx.Choice(panel, choices=[f"摄像头 {i}" for i in range(count_cameras())])
        self.camera_choice.SetSelection(0)
        self.camera_choice.Bind(wx.EVT_CHOICE, self.on_camera_change)
        vbox.Add(self.camera_choice, flag=wx.EXPAND | wx.ALL, border=10)

        # 显示区域
        self.camera_panel = CameraPanel(panel, desired_width=1920, desired_height=1080, camera_index=0)
        vbox.Add(self.camera_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_camera_change(self, event):
        index = self.camera_choice.GetSelection()
        if self.camera_panel:
            self.camera_panel.stop()
            self.camera_panel.Destroy()
        self.camera_panel = CameraPanel(self, desired_width=1920, desired_height=1080, camera_index=index)
        self.GetSizer().Add(self.camera_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        self.Layout()

    def on_close(self, event):
        if self.camera_panel:
            self.camera_panel.stop()
        self.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = CameraFrame()
    frame.Show()
    app.MainLoop()
