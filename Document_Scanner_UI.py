# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class Main_Ui_Frame
###########################################################################

class Main_Ui_Frame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"高拍仪"), pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.Size( 1024,768 ), wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        top_Sizer = wx.BoxSizer( wx.HORIZONTAL )

        top_left_bSizer = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap_camera = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_bitmap_camera.SetMinSize( wx.Size( 1024,768 ) )

        top_left_bSizer.Add( self.m_bitmap_camera, 10, wx.ALL, 5 )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        m_comboBox_select_cameraChoices = []
        self.m_comboBox_select_camera = wx.ComboBox( self, wx.ID_ANY, _(u"1"), wx.DefaultPosition, wx.DefaultSize, m_comboBox_select_cameraChoices, 0 )
        self.m_comboBox_select_camera.SetSelection( 0 )
        bSizer8.Add( self.m_comboBox_select_camera, 0, wx.ALL, 5 )

        m_comboBox_select_camera_resolutionChoices = []
        self.m_comboBox_select_camera_resolution = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_comboBox_select_camera_resolutionChoices, 0 )
        bSizer8.Add( self.m_comboBox_select_camera_resolution, 0, wx.ALL, 5 )


        bSizer8.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_checkBox_show_camera2_image = wx.CheckBox( self, wx.ID_ANY, _(u"显示副头图像"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_checkBox_show_camera2_image, 0, wx.ALL, 5 )

        self.m_checkBox_detect_squares = wx.CheckBox( self, wx.ID_ANY, _(u"识别"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_checkBox_detect_squares, 0, wx.ALL, 5 )

        self.m_checkBox_rectify_surface = wx.CheckBox( self, wx.ID_ANY, _(u"曲面展平"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_checkBox_rectify_surface, 0, wx.ALL, 5 )

        self.m_button_left_roate = wx.Button( self, wx.ID_ANY, _(u"左旋90"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_button_left_roate, 0, wx.ALL, 5 )

        self.m_button_right_roate = wx.Button( self, wx.ID_ANY, _(u"右旋90"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_button_right_roate, 0, wx.ALL, 5 )


        top_left_bSizer.Add( bSizer8, 0, wx.EXPAND, 5 )


        top_Sizer.Add( top_left_bSizer, 5, wx.EXPAND, 5 )

        top_right_bSizer = wx.BoxSizer( wx.VERTICAL )

        self.m_bmToggleBtn1 = wx.BitmapToggleButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        top_right_bSizer.Add( self.m_bmToggleBtn1, 0, wx.ALL, 5 )

        self.m_bmToggleBtn2 = wx.BitmapToggleButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        top_right_bSizer.Add( self.m_bmToggleBtn2, 0, wx.ALL, 5 )

        self.m_bmToggleBtn3 = wx.BitmapToggleButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        top_right_bSizer.Add( self.m_bmToggleBtn3, 0, wx.ALL, 5 )

        self.m_bmToggleBtn4 = wx.BitmapToggleButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        top_right_bSizer.Add( self.m_bmToggleBtn4, 0, wx.ALL, 5 )


        top_Sizer.Add( top_right_bSizer, 1, wx.EXPAND, 5 )


        bSizer1.Add( top_Sizer, 1, wx.EXPAND, 5 )

        bottom_Sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button_take_photo = wx.Button( self, wx.ID_ANY, _(u"拍照"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        bottom_Sizer.Add( self.m_button_take_photo, 0, wx.ALL, 5 )

        self.m_button_take_doc = wx.Button( self, wx.ID_ANY, _(u"文档"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        bottom_Sizer.Add( self.m_button_take_doc, 0, wx.ALL, 5 )

        self.m_button_merge_photos = wx.Button( self, wx.ID_ANY, _(u"合并图片"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        bottom_Sizer.Add( self.m_button_merge_photos, 0, wx.ALL, 5 )

        self.m_button_scan_qr_code = wx.Button( self, wx.ID_ANY, _(u"读取二维码"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        bottom_Sizer.Add( self.m_button_scan_qr_code, 0, wx.ALL, 5 )

        self.m_button_take_pdf_doc = wx.Button( self, wx.ID_ANY, _(u"单页pdf"), wx.DefaultPosition, wx.Size( 75,75 ), 0 )
        bottom_Sizer.Add( self.m_button_take_pdf_doc, 0, wx.ALL, 5 )


        bSizer1.Add( bottom_Sizer, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        self.m_timer = wx.Timer()
        self.m_timer.SetOwner( self, self.m_timer.GetId() )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.m_checkBox_detect_squares.Bind( wx.EVT_CHECKBOX, self.on_detect_squares )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_detect_squares( self, event ):
        event.Skip()


