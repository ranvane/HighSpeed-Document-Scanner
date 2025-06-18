import wx
import os
import shutil
from wx.lib.scrolledpanel import ScrolledPanel
from send2trash import send2trash


class Thumbnail(wx.Panel):
    def __init__(self, parent, image_path, gallery, thumb_max_size):
        super().__init__(parent)
        self.parent = parent
        self.image_path = image_path
        self.gallery = gallery
        self.selected = False
        self.hidden = False
        self.group_name = None
        self.thumb_max_size = thumb_max_size

        image = wx.Image(image_path)
        image.Rescale(*self._scale_image(image.GetSize(), self.thumb_max_size), wx.IMAGE_QUALITY_HIGH)
        bmp = image.ConvertToBitmap()

        # 顶部显示：序号 + 文件名
        filename = os.path.basename(self.image_path)
        self.top_label = wx.StaticText(self, label=filename, style=wx.ALIGN_CENTER)
        self.top_label.Wrap(self.thumb_max_size[0])  # 自动换行

        self.bmp_ctrl = wx.StaticBitmap(self, bitmap=bmp)
        self.label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        self.label.Hide()

        for ctrl in [self, self.bmp_ctrl, self.label, self.top_label]:
            ctrl.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        self.border = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.top_label, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 2)
        self.border.Add(self.bmp_ctrl, 0, wx.ALL | wx.CENTER, 2)
        self.border.Add(self.label, 0, wx.CENTER | wx.BOTTOM, 2)

        self.SetSizer(self.border)
        self.SetBackgroundColour(wx.NullColour)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def _scale_image(self, size, max_size):
        w, h = size
        mw, mh = max_size
        scale = min(mw / w, mh / h)
        return int(w * scale), int(h * scale)

    def on_click(self, event):
        mods = wx.GetKeyState(wx.WXK_CONTROL) or wx.GetKeyState(wx.WXK_SHIFT)
        self.gallery.toggle_selection(self, multi=mods)

    def on_right_click(self, event):
        if not self.selected:
            self.gallery.toggle_selection(self, multi=False)
        global_pos = self.ClientToScreen(event.GetPosition())
        gallery_pos = self.gallery.scroll.ScreenToClient(global_pos)
        self.gallery.show_context_menu(gallery_pos)
        event.Skip()

    def on_paint(self, event):
        if self.selected:
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen(wx.BLUE, 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            w, h = self.GetSize()
            dc.DrawRectangle(1, 1, w - 2, h - 2)
        event.Skip()

    def set_selected(self, selected: bool):
        self.selected = selected
        self.Refresh()

    def set_group(self, name):
        self.group_name = name
        self.label.SetLabel(name)
        self.label.Show()
        self.Layout()

    def hide(self):
        self.hidden = True
        self.Hide()
        wx.CallAfter(self.gallery.Layout)
        wx.CallAfter(self.gallery.scroll.FitInside)

    def set_index(self, index):
        filename = os.path.basename(self.image_path)
        self.top_label.SetLabel(f"{index}. {filename}")
        self.Layout()


class ThumbnailGallery(wx.Panel):
    def __init__(self, parent, thumb_max_size=(256, 256)):
        super().__init__(parent)
        self.thumb_max_size = thumb_max_size

        self.scroll = ScrolledPanel(self, style=wx.VSCROLL)
        self.scroll.SetupScrolling(scroll_x=False, scroll_y=True)
        self.scroll.SetScrollRate(10, 10)

        self.grid = wx.BoxSizer(wx.VERTICAL)
        self.scroll.SetSizer(self.grid)

        self.thumbnails = []
        self.selected = []

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.scroll, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def add_image(self, path,group_name=None):
        index = len(self.thumbnails) + 1
        thumb = Thumbnail(self.scroll, path, self, self.thumb_max_size)
        if group_name:
            thumb.set_group(group_name)
        thumb.set_index(index)
        self.thumbnails.append(thumb)
        self.grid.Add(thumb, 0, wx.ALL | wx.EXPAND, 4)
        wx.CallAfter(self.scroll.FitInside)
        wx.CallAfter(self.scroll.Layout)
    def get_images(self):
        return [thumb.image_path for thumb in self.thumbnails]

    def toggle_selection(self, thumb, multi=False):
        if not multi:
            for t in self.selected:
                t.set_selected(False)
            self.selected = [thumb]
        else:
            if thumb in self.selected:
                self.selected.remove(thumb)
                thumb.set_selected(False)
            else:
                self.selected.append(thumb)
                thumb.set_selected(True)
        thumb.set_selected(True)

    def show_context_menu(self, pos):
        menu = wx.Menu()
        if len(self.selected) == 1:
            menu.Append(wx.ID_DELETE, "删除")
            menu.Append(101, "重命名")
            menu.Append(102, "不显示")
        elif len(self.selected) > 1:
            menu.Append(103, "分组保存")
            menu.Append(wx.ID_DELETE, "删除")
            menu.Append(102, "不显示")

        self.Bind(wx.EVT_MENU, self.on_menu)
        self.scroll.PopupMenu(menu, pos)
        menu.Destroy()

    def on_menu(self, event):
        evt_id = event.GetId()

        if evt_id == wx.ID_DELETE:
            thumbs_to_remove = list(self.selected)
            self.selected.clear()
            for thumb in thumbs_to_remove:
                try:
                    if os.path.exists(thumb.image_path):
                        send2trash(thumb.image_path)
                    self.thumbnails.remove(thumb)
                    wx.CallAfter(thumb.Destroy)
                except Exception as e:
                    print("删除失败：", e)

        elif evt_id == 101 and len(self.selected) == 1:
            thumb = self.selected[0]
            dlg = wx.TextEntryDialog(self, "输入新文件名：", "重命名")
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue()
                dir_path = os.path.dirname(thumb.image_path)
                ext = os.path.splitext(thumb.image_path)[1]
                new_path = os.path.join(dir_path, new_name + ext)
                try:
                    os.rename(thumb.image_path, new_path)
                    thumb.image_path = new_path
                    thumb.set_index(self.thumbnails.index(thumb) + 1)
                except Exception as e:
                    wx.MessageBox(f"重命名失败: {e}", "错误", wx.ICON_ERROR)
            dlg.Destroy()

        elif evt_id == 102:
            for thumb in self.selected:
                wx.CallAfter(thumb.hide)

        elif evt_id == 103:
            dlg = wx.TextEntryDialog(self, "输入分组名（新目录名）：", "分组保存")
            if dlg.ShowModal() == wx.ID_OK:
                group_name = dlg.GetValue()
                base_dir = os.path.dirname(self.selected[0].image_path)
                group_dir = os.path.join(base_dir, group_name)
                os.makedirs(group_dir, exist_ok=True)

                for thumb in self.selected:
                    new_path = os.path.join(group_dir, os.path.basename(thumb.image_path))
                    try:
                        shutil.move(thumb.image_path, new_path)
                        thumb.image_path = new_path
                        wx.CallAfter(thumb.set_group, group_name)
                        thumb.set_index(self.thumbnails.index(thumb) + 1)
                    except Exception as e:
                        wx.MessageBox(f"分组保存失败: {e}", "错误", wx.ICON_ERROR)
            dlg.Destroy()

        self.selected.clear()
        wx.CallAfter(self.scroll.Layout)
        wx.CallAfter(self.scroll.FitInside)


class MyApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, title="Thumbnail Gallery", size=(265, 600))
        self.gallery = ThumbnailGallery(frame, thumb_max_size=(300, 300))

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

