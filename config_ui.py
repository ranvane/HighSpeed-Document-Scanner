import wx
import app_config  # 之前写好的配置模块


class ConfigFrame(wx.Frame):
    def __init__(self, parent=None, title="参数设置"):
        super().__init__(parent, title=title, size=(600, 500))
        

        self.config = app_config.get_config()
        self.labels = app_config.get_labels_from_config(self.config)

        # 保存输入框控件，key对应 section.option
        self.ctrl_dict = {}

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self._build_ui()

        self.panel.SetSizer(self.vbox)
        
        self.Center()# 居中显示
        # self.Fit()  # 自动调整窗口大小以适配内容
        self.Show()
        
        

    def _build_ui(self):
        # 清空控件，支持刷新UI
        self.vbox.Clear(True)
        self.ctrl_dict.clear()

        # 遍历所有节和参数
        for section in self.config.sections():
            if section == 'LABELS':
                continue  # 不显示标签节

            # 小节标题
            st_section = wx.StaticText(self.panel, label=section)
            font = st_section.GetFont()
            font.PointSize += 4
            font = font.Bold()
            st_section.SetFont(font)
            self.vbox.Add(st_section, flag=wx.LEFT | wx.TOP, border=10)

            grid_sizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=6)
            grid_sizer.AddGrowableCol(1)

            for option, value in self.config.items(section):
                label_text = self.labels.get(option, option)
                label = wx.StaticText(self.panel, label=label_text)
                txt_ctrl = wx.TextCtrl(self.panel, value=value)

                grid_sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
                grid_sizer.Add(txt_ctrl, flag=wx.EXPAND)

                # 保存控件，key格式 section.option
                self.ctrl_dict[f"{section}.{option}"] = txt_ctrl

            self.vbox.Add(grid_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # 按钮区
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_save = wx.Button(self.panel, label="保存")
        btn_reset = wx.Button(self.panel, label="重置默认")

        btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        btn_reset.Bind(wx.EVT_BUTTON, self.on_reset)

        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(btn_save, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_reset)

        self.vbox.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=15)

        self.panel.Layout()

    def on_save(self, event):
        # 遍历控件保存配置
        for key, ctrl in self.ctrl_dict.items():
            section, option = key.split('.', 1)
            value = ctrl.GetValue().strip()
            self.config.set(section, option, value)

        app_config.save_config(self.config)
        wx.MessageBox("配置已保存！", "提示", wx.OK | wx.ICON_INFORMATION)

    def on_reset(self, event):
        # 重置默认配置并刷新界面
        app_config.reset_config_to_default()
        self.config = app_config.get_config()
        self.labels = app_config.get_labels_from_config(self.config)
        self._build_ui()
        self.panel.Layout()
        wx.MessageBox("已重置为默认配置！", "提示", wx.OK | wx.ICON_INFORMATION)


if __name__ == "__main__":
    app = wx.App()
    frame = ConfigFrame()
    app.MainLoop()
