import wx
import app_config
import os


class ConfigFrame(wx.Frame):
    def __init__(self, parent=None, title="参数设置"):
        super().__init__(parent, title=title, size=(650, 590))
        self.SetBackgroundColour(wx.Colour(250, 250, 250))

        self.config = app_config.get_config()
        self.labels = app_config.get_labels_from_config(self.config)

        self.ctrl_dict = {}

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self._build_ui()

        self.panel.SetSizer(self.vbox)
        self.Center()
        self.Show()

    def _build_ui(self):
        self.vbox.Clear(True)
        self.ctrl_dict.clear()

        for section in self.config.sections():
            if section == 'LABELS':
                continue

            box = wx.StaticBox(self.panel, label=section)
            box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

            grid_sizer = wx.FlexGridSizer(cols=3, hgap=10, vgap=6)
            grid_sizer.AddGrowableCol(1)

            for option, value in self.config.items(section):
                label_text = self.labels.get(option, option)
                label = wx.StaticText(self.panel, label=label_text)

                ctrl_type = app_config.get_option_control_type(option)
                ctrl = None
                browse_btn = None

                if ctrl_type == 'folder_picker':
                    ctrl = wx.TextCtrl(self.panel, value=value)
                    browse_btn = wx.Button(self.panel, label="选择...", size=(60, -1))
                    browse_btn.Bind(wx.EVT_BUTTON, lambda evt, c=ctrl: self.select_folder(evt, c))

                elif ctrl_type == 'checkbox':
                    ctrl = wx.CheckBox(self.panel)
                    ctrl.SetValue(value.lower() in ['1', 'true', 'yes'])

                else:  # 默认 text
                    ctrl = wx.TextCtrl(self.panel, value=value)

                self.ctrl_dict[f"{section}.{option}"] = ctrl

                grid_sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
                grid_sizer.Add(ctrl, flag=wx.EXPAND)

                if browse_btn:
                    grid_sizer.Add(browse_btn)
                else:
                    grid_sizer.AddSpacer(1)

            box_sizer.Add(grid_sizer, flag=wx.EXPAND | wx.ALL, border=10)
            self.vbox.Add(box_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

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

    def select_folder(self, event, text_ctrl):
        dlg = wx.DirDialog(self, "选择文件夹", defaultPath=text_ctrl.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            text_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy()

    def validate_input(self):
        errors = []

        def is_int(value):
            try:
                return int(value) >= 0
            except ValueError:
                return False

        for key, ctrl in self.ctrl_dict.items():
            section, option = key.split('.', 1)

            if isinstance(ctrl, wx.CheckBox):
                continue  # 布尔字段无需验证

            value = ctrl.GetValue().strip()

            if option in ('dpi', 'merge_image_interval', 'usb_index'):
                if not is_int(value):
                    errors.append(f"{self.labels.get(option, option)} 应为正整数")

            elif option in ('save_location', 'temp_location'):
                if not value or not os.path.isdir(value):
                    errors.append(f"{self.labels.get(option, option)} 路径无效")

        if errors:
            wx.MessageBox("\n".join(errors), "输入错误", wx.OK | wx.ICON_ERROR)
            return False
        return True

    def on_save(self, event):
        if not self.validate_input():
            return

        for key, ctrl in self.ctrl_dict.items():
            section, option = key.split('.', 1)
            if isinstance(ctrl, wx.CheckBox):
                value = '1' if ctrl.GetValue() else '0'
            else:
                value = ctrl.GetValue().strip()
            self.config.set(section, option, value)

        app_config.save_config(self.config)
        wx.MessageBox("配置已保存！", "提示", wx.OK | wx.ICON_INFORMATION)

    def on_reset(self, event):
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
