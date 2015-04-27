# coding=utf-8
__author__ = 'nico'

import wx

from view.wxUtils import ConfirmDialog, ErrorDialog
from config import MAIN_ICON
from Utils import valid_ip


class ConfWindow(wx.Frame):
    """
    Window that allows user to config general parameters.
    :param parent: Main gVARVI window
    :param title: Title of the window
    :param control: A reference to business logic facade.
    """

    def __init__(self, parent, title, control):
        self.controller = control
        self.conf = self.controller.conf

        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER, title=title, size=(400, 420))

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.CenterOnScreen()

        self.mainPanel = wx.Panel(self)
        self.MinSize = (400, 420)
        self.MaxSize = self.MinSize

        sizer = wx.BoxSizer(wx.VERTICAL)

        general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        default_mode_label = wx.StaticText(self.mainPanel, label='Default mode')
        self.default_mode_list_box = wx.ListBox(self.mainPanel,
                                                size=(175, -1),
                                                choices=["Device connected mode", "Demo mode"])

        if self.conf.defaultMode == "Device connected mode":
            self.default_mode_list_box.Select(0)
        else:
            self.default_mode_list_box.Select(1)

        bluetooth_support_label = wx.StaticText(self.mainPanel, label='Bluetooth support')
        self.bluetooth_support_check_box = wx.CheckBox(self.mainPanel)
        if self.conf.bluetoothSupport == "Yes":
            self.bluetooth_support_check_box.SetValue(state=True)
        else:
            self.bluetooth_support_check_box.SetValue(state=False)

        ant_support_label = wx.StaticText(self.mainPanel, label='ANT+ support')
        self.ant_support_check_box = wx.CheckBox(self.mainPanel)
        if self.conf.antSupport == "Yes":
            self.ant_support_check_box.SetValue(state=True)
        else:
            self.ant_support_check_box.SetValue(state=False)

        scan_devices_on_startup_label = wx.StaticText(self.mainPanel, label='Scan devices on startup')
        self.scan_devices_on_startup_check_box = wx.CheckBox(self.mainPanel)
        if self.conf.scanDevicesOnStartup == "Yes":
            self.scan_devices_on_startup_check_box.SetValue(state=True)
        else:
            self.scan_devices_on_startup_check_box.SetValue(state=False)

        remote_debugger_label = wx.StaticText(self.mainPanel, label='Remote debugger')
        self.remote_debugger_check_box = wx.CheckBox(self.mainPanel)
        if self.conf.remoteDebugger == "Yes":
            self.remote_debugger_check_box.SetValue(state=True)
        else:
            self.remote_debugger_check_box.SetValue(state=False)

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRemoteDebugger, id=self.remote_debugger_check_box.GetId())

        rd_ip_label = wx.StaticText(self.mainPanel, label='Remote debugger IP')
        self.rd_ip_text_ctrl = wx.TextCtrl(self.mainPanel, -1, size=(175, -1), value=self.conf.rdIP)
        if self.conf.remoteDebugger == "No":
            self.rd_ip_text_ctrl.Disable()

        rd_port_label = wx.StaticText(self.mainPanel, label='Remote debugger port')
        self.rd_port_text_ctrl = wx.SpinCtrl(self.mainPanel, value=str(self.conf.rdPort), min=1025, max=65535)
        if self.conf.remoteDebugger == "No":
            self.rd_port_text_ctrl.Disable()

        general_data_sizer.AddMany(
            [default_mode_label, self.default_mode_list_box,
             bluetooth_support_label, self.bluetooth_support_check_box,
             ant_support_label, self.ant_support_check_box,
             scan_devices_on_startup_label, self.scan_devices_on_startup_check_box,
             remote_debugger_label, self.remote_debugger_check_box,
             rd_ip_label, self.rd_ip_text_ctrl,
             rd_port_label, self.rd_port_text_ctrl])

        static_line = wx.StaticLine(self.mainPanel, -1, size=(1, 1), style=wx.LI_HORIZONTAL)
        static_line.SetForegroundColour(wx.Colour(255, 0, 255))

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        button_save = wx.Button(self.mainPanel, -1, label="Save")
        buttons_sizer.Add(button_save, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnSavePreferences, id=button_save.GetId())
        button_save.SetToolTip(wx.ToolTip("Save preferences"))

        button_cancel = wx.Button(self.mainPanel, -1, label="Cancel")
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip("Return to the main window"))

        button_reset = wx.Button(self.mainPanel, -1, label="Reset")
        buttons_sizer.Add(button_reset, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnResetPreferences, id=button_reset.GetId())
        button_reset.SetToolTip(wx.ToolTip("Back to the default configuration"))

        sizer.Add(general_data_sizer, 1, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(static_line, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(buttons_sizer, 0, wx.CENTER | wx.BOTTOM, border=10)

        self.mainPanel.SetSizer(sizer)

    def OnCheckRemoteDebugger(self, _):
        if self.remote_debugger_check_box.IsChecked():
            self.rd_ip_text_ctrl.Enable()
            self.rd_port_text_ctrl.Enable()
        else:
            self.rd_ip_text_ctrl.Disable()
            self.rd_port_text_ctrl.Disable()

    def OnSavePreferences(self, _):
        new_config = self.controller.conf
        new_config.defaultMode = self.default_mode_list_box.GetStringSelection()
        new_config.bluetoothSupport = "Yes" if self.bluetooth_support_check_box.IsChecked() else "No"
        new_config.antSupport = "Yes" if self.ant_support_check_box.IsChecked() else "No"

        new_config.scanDevicesOnStartup = "Yes" if self.scan_devices_on_startup_check_box.IsChecked() else "No"
        new_config.remoteDebugger = "Yes" if self.remote_debugger_check_box.IsChecked() else "No"

        new_config.rdIP = self.rd_ip_text_ctrl.GetValue()
        if valid_ip(new_config.rdIP):
            new_config.rdPort = self.rd_port_text_ctrl.GetValue()
            self.controller.save_config()
            if new_config.remoteDebugger == "Yes":
                self.controller.activate_remote_debug(new_config.rdIP, int(new_config.rdPort))
            else:
                self.controller.deactivate_remote_debug()
            self.Destroy()
        else:
            ErrorDialog("Remote debugger IP field must be a valid ip, although it had not been activated.").show()

    def OnCancel(self, _):
        self.Destroy()

    def OnResetPreferences(self, _):
        result = ConfirmDialog("Are you sure to reset preferences?", "Confirm").get_result()
        if result == wx.ID_YES:
            self.controller.reset_config()
            self.Destroy()