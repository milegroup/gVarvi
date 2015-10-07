# coding=utf-8
__author__ = 'nico'

import wx
import sys
import os

from view.wxutils import ErrorDialog
from utils import get_translation

_ = get_translation()


class EndedAcquisitionDialog(wx.Frame):
    """
    Window shown to the user when acquisition finishes.
    @param parent: Main window of gVARVI.
    @param main_facade: Main application facade.
    """

    def __init__(self, parent, main_facade, title):
        wx.Frame.__init__(self, parent, title=title, size=(265, 220))
        self.main_facade = main_facade
        self.main_panel = wx.Panel(self)

        internal_sizer = wx.BoxSizer(wx.VERTICAL)

        options_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)
        ghrv_label = wx.StaticText(self.main_panel, label=_('Open in gHRV'))
        self.ghrv_check_box = wx.CheckBox(self.main_panel)
        plot_label = wx.StaticText(self.main_panel, label=_('Plot results'))
        self.plot_check_box = wx.CheckBox(self.main_panel)
        open_tag_file_label = wx.StaticText(self.main_panel, label=_('Open tag file'))
        self.open_tag_file_check_box = wx.CheckBox(self.main_panel)
        open_rr_file_label = wx.StaticText(self.main_panel, label=_('Open rr file'))
        self.open_rr_file_check_box = wx.CheckBox(self.main_panel)

        options_sizer.AddMany(
            [ghrv_label, self.ghrv_check_box,
             plot_label, self.plot_check_box,
             open_tag_file_label, self.open_tag_file_check_box,
             open_rr_file_label, self.open_rr_file_check_box]
        )

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self.main_panel, label=_('OK'))
        ok_btn.Bind(wx.EVT_BUTTON, self._OnOK)
        button_sizer.Add(ok_btn, 0, wx.CENTER | wx.BOTTOM)

        internal_sizer.Add(options_sizer, 1, wx.ALL | wx.CENTER, border=20)
        internal_sizer.Add(button_sizer, 1, wx.CENTER)

        self.main_panel.SetSizer(internal_sizer)
        self.Centre()

    def _OnOK(self, _):

        # ---- Non blocking operations --
        if self.ghrv_check_box.IsChecked():
            self._OnGHRV()
        if self.open_rr_file_check_box.IsChecked():
            self._OnOpenRRFile()
        if self.open_tag_file_check_box.IsChecked():
            self._OnOpenTagFile()
        # -------------------------------

        # - Blocking operation must be after non blocking ones -
        if self.plot_check_box.IsChecked():
            self._OnPlotResults()
        # ------------------------------------------------------

        self.Destroy()

    def _OnGHRV(self):
        sysplat = sys.platform
        if sysplat == "linux2":
            sysexec_ghrv = "/usr/bin/gHRV"
            if os.path.isfile(sysexec_ghrv):
                self.main_facade.open_ghrv()
            else:
                ErrorDialog(_("gHRV must be installed in the system")).show()
        elif sysplat == "win32" or sysplat == "darwin":
            ErrorDialog(_("This feature is only available for Linux platforms")).show()

    def _OnOpenRRFile(self):
        self.main_facade.open_rr_file()

    def _OnOpenTagFile(self):
        self.main_facade.open_tag_file()

    def _OnPlotResults(self):
        self.main_facade.plot_results()
