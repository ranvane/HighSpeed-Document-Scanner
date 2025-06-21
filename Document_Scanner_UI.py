# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from ThumbnailGallery import ThumbnailGallery

import gettext
_ = gettext.gettext

###########################################################################
## Class Main_Ui_Frame
###########################################################################

class Main_Ui_Frame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"高拍仪"), pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.Size( 1024,768 ), wx.DefaultSize )
        self.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        top_Sizer = wx.BoxSizer( wx.HORIZONTAL )

        top_Sizer.SetMinSize( wx.Size( 1024,1000 ) )
        top_left_bSizer = wx.BoxSizer( wx.VERTICAL )

        top_left_bSizer.SetMinSize( wx.Size( 1024,1000 ) )
        self.m_bitmap_camera = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_bitmap_camera.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_bitmap_camera.SetMinSize( wx.Size( 1024,768 ) )
        self.m_bitmap_camera.SetMaxSize( wx.Size( 1920,1080 ) )

        top_left_bSizer.Add( self.m_bitmap_camera, 10, wx.ALL|wx.EXPAND, 5 )

        m_item_bSizer = wx.BoxSizer( wx.HORIZONTAL )

        m_item_bSizer.SetMinSize( wx.Size( 1024,50 ) )
        m_comboBox_select_cameraChoices = []
        self.m_comboBox_select_camera = wx.ComboBox( self, wx.ID_ANY, _(u"1"), wx.DefaultPosition, wx.DefaultSize, m_comboBox_select_cameraChoices, 0 )
        self.m_comboBox_select_camera.SetSelection( 0 )
        self.m_comboBox_select_camera.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_comboBox_select_camera, 0, wx.ALL|wx.EXPAND, 5 )

        m_comboBox_select_camera_resolutionChoices = []
        self.m_comboBox_select_camera_resolution = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_comboBox_select_camera_resolutionChoices, 0 )
        self.m_comboBox_select_camera_resolution.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_comboBox_select_camera_resolution, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_web_camera_address = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
        self.m_web_camera_address.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_web_camera_address.Hide()

        m_item_bSizer.Add( self.m_web_camera_address, 0, wx.ALL, 5 )

        self.m_checkBox_web_camera = wx.CheckBox( self, wx.ID_ANY, _(u"使用网络摄像头"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox_web_camera.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_checkBox_web_camera, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_TextCtrl_GroupName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), 0 )
        self.m_TextCtrl_GroupName.SetMaxLength( 150 )
        self.m_TextCtrl_GroupName.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_TextCtrl_GroupName.Enable( False )

        m_item_bSizer.Add( self.m_TextCtrl_GroupName, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_checkBox_saveByGroup = wx.CheckBox( self, wx.ID_ANY, _(u"分组保存"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox_saveByGroup.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_checkBox_saveByGroup, 0, wx.ALL|wx.EXPAND, 5 )


        m_item_bSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_checkBox_show_camera2_image = wx.CheckBox( self, wx.ID_ANY, _(u"显示副头图像"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox_show_camera2_image.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_checkBox_show_camera2_image, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_checkBox_detect_squares = wx.CheckBox( self, wx.ID_ANY, _(u"识别"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox_detect_squares.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_checkBox_detect_squares, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_checkBox_rectify_surface = wx.CheckBox( self, wx.ID_ANY, _(u"曲面展平"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox_rectify_surface.SetValue(True)
        self.m_checkBox_rectify_surface.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_checkBox_rectify_surface, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_button_left_rotation = wx.Button( self, wx.ID_ANY, _(u"左旋90"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_left_rotation.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_button_left_rotation, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_button_right_rotation = wx.Button( self, wx.ID_ANY, _(u"右旋90"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_right_rotation.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        m_item_bSizer.Add( self.m_button_right_rotation, 0, wx.ALL|wx.EXPAND, 5 )


        top_left_bSizer.Add( m_item_bSizer, 0, wx.EXPAND, 5 )


        top_Sizer.Add( top_left_bSizer, 5, wx.ALL|wx.EXPAND, 5 )

        top_right_bSizer = wx.BoxSizer( wx.VERTICAL )

        top_right_bSizer.SetMinSize( wx.Size( 270,1000 ) )
        self.m_thumbnailgallery = ThumbnailGallery(self)
        self.m_thumbnailgallery.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_thumbnailgallery.SetMinSize( wx.Size( 260,1000 ) )

        top_right_bSizer.Add( self.m_thumbnailgallery, 1, wx.ALL|wx.EXPAND, 5 )


        top_Sizer.Add( top_right_bSizer, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer1.Add( top_Sizer, 0, wx.EXPAND, 5 )

        bottom_Sizer = wx.BoxSizer( wx.HORIZONTAL )

        bottom_Sizer.SetMinSize( wx.Size( 1024,80 ) )
        self.m_button_take_photo = wx.Button( self, wx.ID_ANY, _(u"拍照"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_take_photo.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_button_take_photo.SetToolTip( _(u"保存原始图像。") )

        bottom_Sizer.Add( self.m_button_take_photo, 0, wx.ALL, 5 )

        self.m_button_take_doc = wx.Button( self, wx.ID_ANY, _(u"矫正为文档"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_take_doc.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_button_take_doc.SetToolTip( _(u"保存提取、矫正后的文档图像。") )

        bottom_Sizer.Add( self.m_button_take_doc, 0, wx.ALL, 5 )

        self.m_button_take_card = wx.Button( self, wx.ID_ANY, _(u"提取证件"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_take_card.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )
        self.m_button_take_card.SetToolTip( _(u"保存提取、矫正后的文档图像。") )

        bottom_Sizer.Add( self.m_button_take_card, 0, wx.ALL, 5 )

        self.m_button_merge_photos = wx.Button( self, wx.ID_ANY, _(u"合并图片"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_merge_photos.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bottom_Sizer.Add( self.m_button_merge_photos, 0, wx.ALL, 5 )

        self.m_button_scan_qr_code = wx.Button( self, wx.ID_ANY, _(u"读取二维码"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_scan_qr_code.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bottom_Sizer.Add( self.m_button_scan_qr_code, 0, wx.ALL, 5 )

        self.m_button_take_pdf_doc = wx.Button( self, wx.ID_ANY, _(u"单页pdf"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_take_pdf_doc.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bottom_Sizer.Add( self.m_button_take_pdf_doc, 0, wx.ALL, 5 )

        self.m_button_take_mutip_pdf_doc = wx.Button( self, wx.ID_ANY, _(u"多页pdf"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_take_mutip_pdf_doc.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bottom_Sizer.Add( self.m_button_take_mutip_pdf_doc, 0, wx.ALL, 5 )


        bottom_Sizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_button_setting = wx.Button( self, wx.ID_ANY, _(u"设置"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        self.m_button_setting.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bottom_Sizer.Add( self.m_button_setting, 0, wx.ALL, 5 )


        bSizer1.Add( bottom_Sizer, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        self.m_statusBar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_statusBar.SetMinSize( wx.Size( -1,30 ) )


        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.m_checkBox_web_camera.Bind( wx.EVT_CHECKBOX, self.on_use_webcam )
        self.m_checkBox_saveByGroup.Bind( wx.EVT_CHECKBOX, self.on_checkBox_saveByGroup )
        self.m_checkBox_detect_squares.Bind( wx.EVT_CHECKBOX, self.on_document_outline_detection )
        self.m_checkBox_rectify_surface.Bind( wx.EVT_CHECKBOX, self.on_rectify_surface )
        self.m_button_left_rotation.Bind( wx.EVT_BUTTON, self.on_left_rotation )
        self.m_button_right_rotation.Bind( wx.EVT_BUTTON, self.on_right_rotation )
        self.m_button_take_photo.Bind( wx.EVT_BUTTON, self.on_take_photo )
        self.m_button_take_doc.Bind( wx.EVT_BUTTON, self.on_take_document )
        self.m_button_take_card.Bind( wx.EVT_BUTTON, self.on_take_card )
        self.m_button_merge_photos.Bind( wx.EVT_BUTTON, self.on_merge_photos )
        self.m_button_scan_qr_code.Bind( wx.EVT_BUTTON, self.on_scan_qr_code )
        self.m_button_take_pdf_doc.Bind( wx.EVT_BUTTON, self.on_take_pdf_doc )
        self.m_button_take_mutip_pdf_doc.Bind( wx.EVT_BUTTON, self.on_take_mutip_pdf_doc )
        self.m_button_setting.Bind( wx.EVT_BUTTON, self.on_setting )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_use_webcam( self, event ):
        event.Skip()

    def on_checkBox_saveByGroup( self, event ):
        event.Skip()

    def on_document_outline_detection( self, event ):
        event.Skip()

    def on_rectify_surface( self, event ):
        event.Skip()

    def on_left_rotation( self, event ):
        event.Skip()

    def on_right_rotation( self, event ):
        event.Skip()

    def on_take_photo( self, event ):
        event.Skip()

    def on_take_document( self, event ):
        event.Skip()

    def on_take_card( self, event ):
        event.Skip()

    def on_merge_photos( self, event ):
        event.Skip()

    def on_scan_qr_code( self, event ):
        event.Skip()

    def on_take_pdf_doc( self, event ):
        event.Skip()

    def on_take_mutip_pdf_doc( self, event ):
        event.Skip()

    def on_setting( self, event ):
        event.Skip()


###########################################################################
## Class Setting_Dialog
###########################################################################

class Setting_Dialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"设置"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"保存路径："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )

        self.m_staticText1.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer9.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.m_save_path = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,-1 ), 0 )
        self.m_save_path.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer9.Add( self.m_save_path, 0, wx.ALL, 5 )

        self.m_select_save_path = wx.Button( self, wx.ID_ANY, _(u"选择"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_select_save_path.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer9.Add( self.m_select_save_path, 0, wx.ALL, 5 )


        bSizer8.Add( bSizer9, 0, wx.EXPAND, 5 )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"命名方式：") ), wx.VERTICAL )

        bSizer91 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_radioBtn_data_and_numbers = wx.RadioButton( sbSizer1.GetStaticBox(), wx.ID_ANY, _(u"日期+数字"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_radioBtn_data_and_numbers.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer91.Add( self.m_radioBtn_data_and_numbers, 1, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        self.m_staticText7.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer91.Add( self.m_staticText7, 1, wx.ALL, 5 )

        self.m_radioBtn_datatime = wx.RadioButton( sbSizer1.GetStaticBox(), wx.ID_ANY, _(u"年月日_时分秒"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_radioBtn_datatime.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer91.Add( self.m_radioBtn_datatime, 1, wx.ALL, 5 )


        sbSizer1.Add( bSizer91, 1, wx.EXPAND, 5 )


        bSizer8.Add( sbSizer1, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"摄像头1分辨率："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )

        self.m_staticText4.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )

        m_choice_camera_resolution1Choices = []
        self.m_choice_camera_resolution1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_camera_resolution1Choices, 0 )
        self.m_choice_camera_resolution1.SetSelection( 0 )
        self.m_choice_camera_resolution1.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer11.Add( self.m_choice_camera_resolution1, 0, wx.ALL, 5 )

        self.m_button_select_camera_resolution1 = wx.Button( self, wx.ID_ANY, _(u"确定"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_select_camera_resolution1.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer11.Add( self.m_button_select_camera_resolution1, 0, wx.ALL, 5 )

        self.m_button_auto_check_camera_resolution1 = wx.Button( self, wx.ID_ANY, _(u"检测支持的分辨率"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_auto_check_camera_resolution1.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer11.Add( self.m_button_auto_check_camera_resolution1, 0, wx.ALL, 5 )


        bSizer8.Add( bSizer11, 0, wx.EXPAND, 5 )

        bSizer111 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText41 = wx.StaticText( self, wx.ID_ANY, _(u"摄像头2分辨率："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText41.Wrap( -1 )

        self.m_staticText41.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer111.Add( self.m_staticText41, 0, wx.ALL, 5 )

        m_choice_camera_resolution2Choices = []
        self.m_choice_camera_resolution2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_camera_resolution2Choices, 0 )
        self.m_choice_camera_resolution2.SetSelection( 0 )
        self.m_choice_camera_resolution2.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer111.Add( self.m_choice_camera_resolution2, 0, wx.ALL, 5 )

        self.m_button_select_camera_resolution2 = wx.Button( self, wx.ID_ANY, _(u"确定"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_select_camera_resolution2.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer111.Add( self.m_button_select_camera_resolution2, 0, wx.ALL, 5 )

        self.m_button_auto_check_camera_resolution2 = wx.Button( self, wx.ID_ANY, _(u"检测支持的分辨率"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_auto_check_camera_resolution2.SetBackgroundColour( wx.Colour( 245, 245, 250 ) )

        bSizer111.Add( self.m_button_auto_check_camera_resolution2, 0, wx.ALL, 5 )


        bSizer8.Add( bSizer111, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer8 )
        self.Layout()
        bSizer8.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


