# coding=utf-8
__author__ = 'nico'

import wx

from InsModPhotoPresentation import InsModPhotoPresentation
from InsModSoundPresentation import InsModSoundPresentation
from InsModVideoPresentation import InsModVideoPresentation
from InsModAssociatedKey import InsModAssociatedKey
from InsModManualDefined import InsModManualDefined
from config import MAIN_ICON, IMAGE_ICON, SOUND_ICON, \
    VIDEO_ICON, MANUAL_ICON, KEY_ICON
from config import BACKGROUND_COLOUR


class AddActivityWindow(wx.Frame):
    def __init__(self, parent, title, main_facade):
        self.parent = parent
        self.main_facade = main_facade
        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER, title=title, size=(900, 265))
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.CenterOnScreen()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        image_tooltip = """Picture presentation activity:
        This activity plays some groups of pictures. Also
        allows to associate sounds to each picture group."""
        image_bitmap = wx.Bitmap(IMAGE_ICON, wx.BITMAP_TYPE_ANY)
        image_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=image_bitmap,
                                       size=(150, 150))
        image_button.SetToolTip(wx.ToolTip(image_tooltip))
        self.Bind(wx.EVT_BUTTON, self._OnImageActivity, id=image_button.GetId())

        video_tooltip = """Video presentation activity:
        This activity plays some individual videos"""
        video_bitmap = wx.Bitmap(VIDEO_ICON, wx.BITMAP_TYPE_ANY)
        video_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=video_bitmap,
                                       size=(150, 150))
        video_button.SetToolTip(wx.ToolTip(video_tooltip))
        self.Bind(wx.EVT_BUTTON, self._OnVideoActivity, id=video_button.GetId())

        sound_tooltip = """Sound presentation activity:
        This activity plays some individual sounds. Also
        allows to associate some images to each sound."""
        sound_bitmap = wx.Bitmap(SOUND_ICON, wx.BITMAP_TYPE_ANY)
        sound_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=sound_bitmap,
                                       size=(150, 150))
        sound_button.SetToolTip(wx.ToolTip(sound_tooltip))
        self.Bind(wx.EVT_BUTTON, self._OnSoundActivity, id=sound_button.GetId())

        manual_tooltip = """Manual activity:
        This activity plays some tags and shows
        on screen a custom text for each tag. The
        user can choose if the tag ends with key
        pressing or with a timeout."""
        manual_bitmap = wx.Bitmap(MANUAL_ICON, wx.BITMAP_TYPE_ANY)
        manual_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=manual_bitmap,
                                        size=(150, 150))
        manual_button.SetToolTip(wx.ToolTip(manual_tooltip))
        self.Bind(wx.EVT_BUTTON, self._OnManualDefinedActivity, id=manual_button.GetId())

        key_tooltip = """Associated key activity:
        This activity plays some tags and shows on
        screen a custom text for each tag. Tags have
        an associated key, so changing tags is as
        simple as press the associated key of next tag."""
        key_bitmap = wx.Bitmap(KEY_ICON, wx.BITMAP_TYPE_ANY)
        key_button = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=key_bitmap,
                                     size=(150, 150))
        key_button.SetToolTip(wx.ToolTip(key_tooltip))
        self.Bind(wx.EVT_BUTTON, self._OnKeyAssociatedActivity, id=key_button.GetId())

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

        line = wx.StaticLine(self, -1, size=(1, 1), style=wx.LI_HORIZONTAL)
        line.SetForegroundColour(wx.Colour(0, 0, 255))

        button_cancel = wx.Button(self, -1, label="Cancel")
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_BUTTON, self._OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip("Return to the main window"))

        main_sizer.AddSpacer(20)
        main_sizer.Add(top_sizer, proportion=1, flag=wx.CENTER)
        main_sizer.AddSpacer(10)
        main_sizer.Add(line, 0, wx.EXPAND | wx.ALL, border=10)
        main_sizer.AddSpacer(10)
        main_sizer.Add(buttons_sizer, proportion=1, flag=wx.CENTER | wx.BOTTOM)
        self.SetSizer(main_sizer)

    def _OnCancel(self, _):
        self.Destroy()

    def _OnImageActivity(self, _):
        InsModPhotoPresentation(self.parent, self.main_facade)
        self.Destroy()

    def _OnVideoActivity(self, _):
        InsModVideoPresentation(self.parent, self.main_facade)
        self.Destroy()

    def _OnSoundActivity(self, _):
        InsModSoundPresentation(self.parent, self.main_facade)
        self.Destroy()

    def _OnManualDefinedActivity(self, _):
        InsModManualDefined(self.parent, self.main_facade)
        self.Destroy()

    def _OnKeyAssociatedActivity(self, _):
        InsModAssociatedKey(self.parent, self.main_facade)
        self.Destroy()