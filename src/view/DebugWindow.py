# -*- coding: utf-8 -*-
__author__ = 'nico'

import wx

from logger import Logger
from Utils import CustomConsoleHandler


class DebugWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Debug Window", size=(400, 400))

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

    def _OnClose(self, e):
        self.Hide()


