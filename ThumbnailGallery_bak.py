import wx
import os
import shutil
from wx.lib.scrolledpanel import ScrolledPanel
from send2trash import send2trash


class Thumbnail(wx.Panel):
    """
    缩略图控件，用于显示图片的缩略图，支持标签显示、选中状态管理等功能。
    """

    def __init__(self, parent, image_path, gallery, thumb_max_size):
        """
        初始化缩略图控件。

        Args:
            parent (wx.Window): 父窗口对象。
            image_path (str): 图片文件的路径。
            gallery (ThumbnailGallery): 所属的缩略图库对象。
            thumb_max_size (tuple): 缩略图的最大尺寸，格式为 (宽度, 高度)。
        """
        super().__init__(parent)
        self.parent = parent
        self.image_path = image_path
        self.gallery = gallery
        self.selected = False  # 标记该缩略图是否被选中
        self.hidden = False    # 标记该缩略图是否被隐藏
        self.group_name = None  # 存储该缩略图所属的分组名
        self.thumb_max_size = thumb_max_size  # 新增：存储缩略图最大尺寸

        # 加载图像并将其缩放为符合最大尺寸要求的缩略图
        image = wx.Image(image_path)
        image.Rescale(*self._scale_image(image.GetSize(), self.thumb_max_size), wx.IMAGE_QUALITY_HIGH)
        bmp = image.ConvertToBitmap()

        # 创建静态位图控件用于显示缩略图
        self.bmp_ctrl = wx.StaticBitmap(self, bitmap=bmp)
        # 创建静态文本控件用于显示标签，初始状态隐藏
        self.label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        self.label.Hide()

        # 为当前面板、位图控件和标签控件绑定鼠标事件
        # 右键点击显示上下文菜单，左键点击处理选中逻辑
        for ctrl in [self, self.bmp_ctrl, self.label]:
            ctrl.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        # 使用垂直布局管理器，依次添加位图控件和标签控件
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.bmp_ctrl, 0, wx.ALL | wx.CENTER, 2)
        self.border.Add(self.label, 0, wx.CENTER | wx.BOTTOM, 2)

        self.SetSizer(self.border)
        self.SetBackgroundColour(wx.NullColour)

        # 绑定绘制事件，用于绘制选中状态的边框
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def _scale_image(self, size, max_size):
        """
        按比例缩放图像尺寸，确保图像在不超出最大尺寸的前提下保持宽高比。

        Args:
            size (tuple): 原始图像的尺寸，格式为 (宽度, 高度)。
            max_size (tuple): 允许的最大尺寸，格式为 (最大宽度, 最大高度)。

        Returns:
            tuple: 缩放后的图像尺寸，格式为 (宽度, 高度)。
        """
        w, h = size
        mw, mh = max_size
        scale = min(mw / w, mh / h)
        return int(w * scale), int(h * scale)

    def on_click(self, event):
        """
        处理左键点击事件，支持 Ctrl 或 Shift 键实现多选功能。

        Args:
            event (wx.Event): 鼠标点击事件对象。
        """
        # 检查是否按下了 Ctrl 或 Shift 键
        mods = wx.GetKeyState(wx.WXK_CONTROL) or wx.GetKeyState(wx.WXK_SHIFT)
        self.gallery.toggle_selection(self, multi=mods)

    def on_right_click(self, event):
        """
        处理右键点击事件，若当前缩略图未选中则先选中，然后显示上下文菜单。

        Args:
            event (wx.Event): 鼠标右键点击事件对象。
        """
        if not self.selected:
            self.gallery.toggle_selection(self, multi=False)

        # 将鼠标点击位置转换为全局坐标
        global_pos = self.ClientToScreen(event.GetPosition())
        # 将全局坐标转换为缩略图库滚动面板的局部坐标
        gallery_pos = self.gallery.scroll.ScreenToClient(global_pos)
        self.gallery.show_context_menu(gallery_pos)
        event.Skip()

    def on_paint(self, event):
        """
        绘制事件处理函数，当缩略图处于选中状态时绘制蓝色边框。

        Args:
            event (wx.Event): 绘制事件对象。
        """
        if self.selected:
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen(wx.BLUE, 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            w, h = self.GetSize()
            dc.DrawRectangle(1, 1, w - 2, h - 2)
        event.Skip()

    def set_selected(self, selected: bool):
        """
        设置缩略图的选中状态，并刷新界面以显示或隐藏边框。

        Args:
            selected (bool): True 表示选中，False 表示取消选中。
        """
        self.selected = selected
        self.Refresh()

    def set_group(self, name):
        """
        设置并显示缩略图所属的分组名标签。

        Args:
            name (str): 分组名。
        """
        self.group_name = name
        self.label.SetLabel(name)
        self.label.Show()
        self.Layout()

    def hide(self):
        """
        隐藏缩略图，并触发缩略图库的布局更新。
        """
        self.hidden = True
        self.Hide()
        wx.CallAfter(self.gallery.Layout)
        wx.CallAfter(self.gallery.scroll.FitInside)


class ThumbnailGallery(wx.Panel):
    """
    图片缩略图库控件，支持批量加载图片、多选、上下文菜单操作等功能。
    """

    def __init__(self, parent, thumb_max_size=(256, 256)):
        """
        初始化缩略图库控件。

        Args:
            parent (wx.Window): 父窗口对象。
            thumb_max_size (tuple, optional): 缩略图的最大尺寸，格式为 (宽度, 高度)。默认值为 (256, 256)。
        """
        super().__init__(parent)
        self.thumb_max_size = thumb_max_size  # 新增：存储缩略图最大尺寸

        # 创建可滚动面板，仅支持垂直滚动
        self.scroll = ScrolledPanel(self, style=wx.VSCROLL)
        self.scroll.SetupScrolling(scroll_x=False, scroll_y=True)
        self.scroll.SetScrollRate(10, 10)

        # 创建垂直布局管理器并设置给滚动面板
        self.grid = wx.BoxSizer(wx.VERTICAL)
        self.scroll.SetSizer(self.grid)

        self.thumbnails = []  # 存储所有的缩略图对象
        self.selected = []    # 存储当前选中的缩略图对象

        # 创建主布局管理器，将滚动面板添加进去
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.scroll, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def add_image(self, path):
        """
        添加单张图片到缩略图库。

        Args:
            path (str): 图片文件的路径。
        """
        thumb = Thumbnail(self.scroll, path, self, self.thumb_max_size)
        self.thumbnails.append(thumb)
        self.grid.Add(thumb, 0, wx.ALL | wx.EXPAND, 4)
        # 异步调用方法，更新滚动面板的布局和尺寸
        wx.CallAfter(self.scroll.FitInside)
        wx.CallAfter(self.scroll.Layout)

    def toggle_selection(self, thumb, multi=False):
        """
        切换缩略图的选中状态，支持单选和多选模式。

        Args:
            thumb (Thumbnail): 要操作的缩略图对象。
            multi (bool): True 表示多选模式，False 表示单选模式。
        """
        if not multi:
            # 单选模式下，取消之前所有选中的缩略图
            for t in self.selected:
                t.set_selected(False)
            self.selected = [thumb]
        else:
            if thumb in self.selected:
                # 若缩略图已选中，则取消选中
                self.selected.remove(thumb)
                thumb.set_selected(False)
            else:
                # 若缩略图未选中，则添加到选中列表
                self.selected.append(thumb)
                thumb.set_selected(True)

        thumb.set_selected(True)

    def show_context_menu(self, pos):
        """
        在指定位置显示右键上下文菜单，根据选中缩略图的数量显示不同的菜单项。

        Args:
            pos (tuple): 菜单显示的位置，格式为 (x, y)。
        """
        menu = wx.Menu()
        if len(self.selected) == 1:
            menu.Append(wx.ID_DELETE, "删除")
            menu.Append(101, "重命名")
            menu.Append(102, "不显示")
        elif len(self.selected) > 1:
            menu.Append(103, "分组保存")
            menu.Append(wx.ID_DELETE, "删除")
            menu.Append(102, "不显示")

        # 绑定菜单事件处理函数
        self.Bind(wx.EVT_MENU, self.on_menu)
        # 在指定位置弹出菜单
        self.scroll.PopupMenu(menu, pos)
        menu.Destroy()

    def on_menu(self, event):
        """
        右键菜单事件处理函数，根据不同的菜单项 ID 执行相应的操作。

        Args:
            event (wx.Event): 菜单事件对象。
        """
        evt_id = event.GetId()

        # 处理删除操作
        if evt_id == wx.ID_DELETE:
            thumbs_to_remove = list(self.selected)
            self.selected.clear()
            for thumb in thumbs_to_remove:
                try:
                    if os.path.exists(thumb.image_path):
                        # 安全删除文件到回收站
                        send2trash(thumb.image_path)  
                    self.thumbnails.remove(thumb)
                    # 异步调用方法销毁缩略图对象
                    wx.CallAfter(thumb.Destroy)
                except Exception as e:
                    print("删除失败：", e)

        # 处理重命名操作，仅在选中单个缩略图时有效
        elif evt_id == 101 and len(self.selected) == 1:
            thumb = self.selected[0]
            # 创建文本输入对话框，提示用户输入新文件名
            dlg = wx.TextEntryDialog(self, "输入新文件名：", "重命名")
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue()
                dir_path = os.path.dirname(thumb.image_path)
                ext = os.path.splitext(thumb.image_path)[1]
                new_path = os.path.join(dir_path, new_name + ext)
                try:
                    os.rename(thumb.image_path, new_path)
                    thumb.image_path = new_path
                except Exception as e:
                    # 显示错误消息框
                    wx.MessageBox(f"重命名失败: {e}", "错误", wx.ICON_ERROR)
            dlg.Destroy()

        # 处理不显示操作
        elif evt_id == 102:
            for thumb in self.selected:
                # 异步调用方法隐藏缩略图
                wx.CallAfter(thumb.hide)

        # 处理分组保存操作
        elif evt_id == 103:
            # 创建文本输入对话框，提示用户输入分组名
            dlg = wx.TextEntryDialog(self, "输入分组名（新目录名）：", "分组保存")
            if dlg.ShowModal() == wx.ID_OK:
                group_name = dlg.GetValue()
                base_dir = os.path.dirname(self.selected[0].image_path)
                group_dir = os.path.join(base_dir, group_name)
                # 创建分组目录，若目录已存在则不报错
                os.makedirs(group_dir, exist_ok=True)

                for thumb in self.selected:
                    new_path = os.path.join(group_dir, os.path.basename(thumb.image_path))
                    try:
                        shutil.move(thumb.image_path, new_path)
                        thumb.image_path = new_path
                        # 异步调用方法设置分组名
                        wx.CallAfter(thumb.set_group, group_name)
                    except Exception as e:
                        # 显示错误消息框
                        wx.MessageBox(f"分组保存失败: {e}", "错误", wx.ICON_ERROR)
            dlg.Destroy()

        # 清空选中列表并更新滚动面板的布局和尺寸
        self.selected.clear()
        wx.CallAfter(self.scroll.Layout)
        wx.CallAfter(self.scroll.FitInside)


class MyApp(wx.App):
    def OnInit(self):
        """
        初始化主程序窗口，创建缩略图库并加载测试图片。

        Returns:
            bool: 初始化成功返回 True。
        """
        frame = wx.Frame(None, title="Thumbnail Gallery", size=(265, 600))
        # 可以在这里传入自定义的缩略图最大尺寸
        self.gallery = ThumbnailGallery(frame, thumb_max_size=(300, 300))

        # 加载本地测试图片（jpg 格式）
        import glob
        for path in glob.glob("testimages/*.jpg"):
            self.gallery.add_image(path)

        frame.Show()
        return True


if __name__ == "__main__":
    MyApp().MainLoop()


##使用方法：
#  wxformbuilder中添加自定义控件，设置控件属性：
#  name：m_thumbnailgallery
#  class：ThumbnailGallery
#  construction: self.m_thumbnailgallery = ThumbnailGallery(self)
#  include: from ThumbnailGallery import ThumbnailGallery

