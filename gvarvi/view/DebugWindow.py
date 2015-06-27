# -*- coding: utf-8 -*-

import wx

from logger import Logger
from utils import CustomConsoleHandler, get_translation

_ = get_translation()

class DebugWindow(wx.Frame):
    """
    Window where logger shows debug data to user.
    :param parent: Reference to MainWindow object
    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=_("Debug Window"), size=(400, 400))

        self.logger = Logger()

        log_text = wx.TextCtrl(self,
                               style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log_text, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        txt_handler = CustomConsoleHandler(log_text)
        self.logger.addHandler(txt_handler)
        self.Bind(wx.EVT_CLOSE, self._OnClose)
        self.Centre()

    def _OnClose(self, _):
        self.Hide()


