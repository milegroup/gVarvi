# coding=utf-8
import wx

from config import BACKGROUND_COLOUR, EVT_RESULT_ID
from utils import get_translation

_ = get_translation()


class TestDeviceFrame(wx.Frame):
    """
    Window to show real time data of acquisition device.
    @param main_facade: Main application facade.
    """

    def __init__(self, main_facade):
        DEFAULT_TITLE_FONT = wx.Font(pointSize=25, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        NORMAL_FONT = wx.Font(pointSize=18, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        self.main_facade = main_facade
        no_close = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=_("Running test"), size=(400, 260), style=no_close)

        self.SetBackgroundColour(BACKGROUND_COLOUR)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSpacer(20)
        self.status_text = wx.StaticText(self, -1, _("Connecting..."))
        self.status_text.SetFont(DEFAULT_TITLE_FONT)
        box.Add(self.status_text, 1, wx.ALIGN_CENTER)
        box.AddSpacer(20)

        results_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)
        rr_label = wx.StaticText(self, label=_('RR Value'))
        rr_label.SetFont(NORMAL_FONT)
        self.rr_text = wx.StaticText(self, label='-')
        self.rr_text.SetFont(NORMAL_FONT)
        hr_label = wx.StaticText(self, label=_('HR Value'))
        hr_label.SetFont(NORMAL_FONT)
        self.hr_text = wx.StaticText(self, label='-')
        self.hr_text.SetFont(NORMAL_FONT)

        results_sizer.AddMany([rr_label, self.rr_text,
                               hr_label, self.hr_text])
        box.Add(results_sizer, proportion=1, flag=wx.ALIGN_CENTER)

        box.AddSpacer(20)

        close_button = wx.Button(self, wx.OK, _("OK"))
        close_button.Bind(wx.EVT_BUTTON, self.OnOk)
        box.Add(close_button, 1, wx.ALIGN_CENTER | wx.CENTER)
        box.AddSpacer(20)
        self.SetSizer(box)
        self.CenterOnScreen()
        self.Show()

    def run_test(self, name, mac, dev_type):
        self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)
        self.main_facade.run_test(notify_window=self, name=name, mac=mac, dev_type=dev_type)

    def OnOk(self, _e):
        self.status_text.SetLabel(_("Disconnecting..."))
        self.Disconnect(-1, -1, EVT_RESULT_ID, self.OnResult)
        wx.CallAfter(self.main_facade.end_device_test)
        wx.CallAfter(self.Destroy)

    def OnResult(self, event):
        result_dict = event.data
        self.rr_text.SetLabel("{0}".format(result_dict['rr']))
        self.hr_text.SetLabel("{0}".format(result_dict['hr']))
        if result_dict['hr'] == 0:
            self.status_text.SetLabel(_("Stabilizing..."))
        else:
            self.status_text.SetLabel(_("Receiving..."))
