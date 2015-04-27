# coding=utf-8
__author__ = 'nico'

import wx

from InsModImageActivity import InsModImageActivity
from InsModSoundActivity import InsModSoundActivity
from InsModVideoActivity import InsModVideoActivity
from view import InsModAssociatedKey
from InsModManualDefined import InsModManualDefined
from config import MAIN_ICON, IMAGE_ICON, SOUND_ICON,\
    VIDEO_ICON, MANUAL_ICON, KEY_ICON
from config import BACKGROUND_COLOUR


class AddActivityWindow(wx.Frame):
    def __init__(self, parent, title, control):
        self.parent = parent
        self.controller = control
        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER, title=title, size=(900, 250))
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.CenterOnScreen()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        image_bitmap = wx.Bitmap(IMAGE_ICON, wx.BITMAP_TYPE_ANY)
        image_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=image_bitmap,
                                       size=(150, 150))
        image_button.SetToolTip(wx.ToolTip("Image presentation"))
        self.Bind(wx.EVT_BUTTON, self.OnImageActivity, id=image_button.GetId())
        video_bitmap = wx.Bitmap(VIDEO_ICON, wx.BITMAP_TYPE_ANY)
        video_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=video_bitmap,
                                       size=(150, 150))
        video_button.SetToolTip(wx.ToolTip("Video presentation"))
        self.Bind(wx.EVT_BUTTON, self.OnVideoActivity, id=video_button.GetId())
        sound_bitmap = wx.Bitmap(SOUND_ICON, wx.BITMAP_TYPE_ANY)
        sound_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=sound_bitmap,
                                       size=(150, 150))
        sound_button.SetToolTip(wx.ToolTip("Sound audition"))
        self.Bind(wx.EVT_BUTTON, self.OnSoundActivity, id=sound_button.GetId())
        manual_bitmap = wx.Bitmap(MANUAL_ICON, wx.BITMAP_TYPE_ANY)
        manual_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=manual_bitmap,
                                        size=(150, 150))
        manual_button.SetToolTip(wx.ToolTip("Manual-defined tagged activity"))
        self.Bind(wx.EVT_BUTTON, self.OnManualDefinedActivity, id=manual_button.GetId())
        key_bitmap = wx.Bitmap(KEY_ICON, wx.BITMAP_TYPE_ANY)
        key_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=key_bitmap,
                                     size=(150, 150))
        key_button.SetToolTip(wx.ToolTip("Associated-Key tagged activity"))
        self.Bind(wx.EVT_BUTTON, self.OnKeyAssociatedActivity, id=key_button.GetId())

        top_sizer.AddSpacer(10)
        top_sizer.Add(image_button, proportion=0, border=20)
        top_sizer.AddSpacer(10)
        top_sizer.Add(video_button, proportion=0, border=20)
        top_sizer.AddSpacer(10)
        top_sizer.Add(sound_button, proportion=0, border=20)
        top_sizer.AddSpacer(10)
        top_sizer.Add(manual_button, proportion=0, border=20)
        top_sizer.AddSpacer(10)
        top_sizer.Add(key_button, proportion=0, border=20)
        top_sizer.AddSpacer(10)

        button_cancel = wx.Button(self, -1, label="Cancel")
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip("Return to the main window"))

        main_sizer.AddSpacer(20)
        main_sizer.Add(top_sizer, proportion=1, flag=wx.CENTER)
        main_sizer.AddSpacer(10)
        main_sizer.Add(buttons_sizer, proportion=1, flag=wx.CENTER | wx.BOTTOM)
        self.SetSizer(main_sizer)

    def OnCancel(self, e):
        self.Destroy()

    def OnImageActivity(self, e):
        InsModImageActivity(self.parent, self.controller)
        self.Destroy()

    def OnVideoActivity(self, e):
        InsModVideoActivity(self.parent, self.controller)
        self.Destroy()

    def OnSoundActivity(self, e):
        InsModSoundActivity(self.parent, self.controller)
        self.Destroy()

    def OnManualDefinedActivity(self, e):
        InsModManualDefined(self.parent, self.controller)
        self.Destroy()

    def OnKeyAssociatedActivity(self, e):
        InsModAssociatedKey(self.parent, self.controller)
        self.Destroy()