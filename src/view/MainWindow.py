# -*- coding: utf-8 -*-

import sys
import os
import threading

from wx import PostEvent
import wx.lib.agw.ultimatelistctrl as ULC

from logger import Logger
from ConfWindow import *
from wxUtils import InfoDialog, ErrorDialog, ConfirmDialog
from config import ACTIVITIES_LIST_ID, DEVICES_LIST_ID, GRID_STYLE, MAIN_ICON, BACKGROUND_COLOUR
from config import DEVICE_CONNECTED_MODE, DEMO_MODE
from Utils import MissingFiles, AbortedAcquisition, FailedAcquisition, HostDownError
from Utils import ResultEvent, EVT_RESULT_ID
from view.DebugWindow import DebugWindow
from view.AddActivityWindow import AddActivityWindow
from view.InsModImageActivity import InsModImageActivity
from view.InsModSoundActivity import InsModSoundActivity
from view.InsModAssociatedKey import InsModAssociatedKey
from view.InsModManualDefined import InsModManualDefined
from view.InsModVideoActivity import InsModVideoActivity


class MainWindow(wx.Frame):
    def __init__(self, parent, title, control):
        self.logger = Logger()

        DEFAULT_TITLE_FONT = wx.Font(pointSize=25, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        self.controller = control

        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title=title, size=(1100, 640))

        self.debug_window = DebugWindow(self)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.CenterOnScreen()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.MinSize = (900, 600)
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("VARVI - MILE Group")

        self.build_menu()

        # ----- Begin of activities box -----

        self.activities_grid_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)

        activities_title = wx.StaticText(self, 0, label="Activities")
        activities_title.SetFont(DEFAULT_TITLE_FONT)
        self.activities_grid_sizer.Add(activities_title, flag=wx.ALIGN_CENTER)
        self.activities_grid = ULC.UltimateListCtrl(self, id=ACTIVITIES_LIST_ID, agwStyle=GRID_STYLE)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectActivity, id=ACTIVITIES_LIST_ID)

        self.activities_grid.SetUserLineHeight(30)

        self.activities_grid.InsertColumn(0, '#', wx.TEXT_ALIGNMENT_CENTER)
        self.activities_grid.SetColumnWidth(0, 30)
        self.activities_grid.InsertColumn(1, 'Name')
        self.activities_grid.SetColumnWidth(1, 200)
        self.activities_grid.InsertColumn(2, 'Type')
        self.activities_grid.SetColumnWidth(2, -3)

        self.activities_grid_sizer.Add(self.activities_grid, proportion=1, flag=wx.EXPAND | wx.ALL, border=20)

        self.activities_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons for adding and removing activities

        buttonAddActivity = wx.Button(self, -1, label="Add")
        self.activities_buttons_sizer.Add(buttonAddActivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnAddActivity, id=buttonAddActivity.GetId())
        buttonAddActivity.SetToolTip(wx.ToolTip("Add new activity"))

        buttonEditActivity = wx.Button(self, -1, label="Edit")
        self.activities_buttons_sizer.Add(buttonEditActivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnEditActivity, id=buttonEditActivity.GetId())
        buttonEditActivity.SetToolTip(wx.ToolTip("Edit the selected activity"))

        buttonRemoveActivity = wx.Button(self, -1, label="Remove")
        self.activities_buttons_sizer.Add(buttonRemoveActivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveActivity, id=buttonRemoveActivity.GetId())
        buttonRemoveActivity.SetToolTip(wx.ToolTip("Remove the selected activity"))

        self.activities_grid_sizer.Add(self.activities_buttons_sizer, proportion=0, flag=wx.CENTER)

        # ----- End of activities box -----


        # ----- Begin of control buttons -----

        external_buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        external_buttons_sizer.Add(wx.StaticLine(self, wx.LI_HORIZONTAL), wx.ALIGN_CENTER | wx.BOTTOM, border=50)
        control_buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label="Global options"), wx.HORIZONTAL)

        button_quit = wx.Button(self, -1, label="Quit")
        control_buttons_sizer.Add(button_quit, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=button_quit.GetId())
        button_quit.SetToolTip(wx.ToolTip("Click to quit using VARVI"))

        button_about = wx.Button(self, -1, label="About")
        control_buttons_sizer.Add(button_about, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, id=button_about.GetId())
        button_about.SetToolTip(wx.ToolTip("Click to see information about VARVI"))

        button_config = wx.Button(self, -1, label="Config")
        control_buttons_sizer.Add(button_config, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnPreferences, id=button_config.GetId())
        button_config.SetToolTip(wx.ToolTip("Click to open configuration window"))

        external_buttons_sizer.Add(control_buttons_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM)

        # ----- End of control buttons -----

        # ----- Begin of Connected Devices List -----

        self.devicesSizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)
        connected_devices_title = wx.StaticText(self, 0, "Connected Devices")
        connected_devices_title.SetFont(DEFAULT_TITLE_FONT)
        self.devicesSizer.Add(connected_devices_title, flag=wx.ALIGN_CENTER)
        self.devicesGrid = ULC.UltimateListCtrl(self, id=DEVICES_LIST_ID, agwStyle=GRID_STYLE)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectDevice, id=DEVICES_LIST_ID)

        self.devicesGrid.SetUserLineHeight(30)
        self.devicesGrid.InsertColumn(0, 'Name')
        self.devicesGrid.SetColumnWidth(0, -3)
        self.devicesGrid.InsertColumn(1, 'MAC')
        self.devicesGrid.SetColumnWidth(1, 140)
        self.devicesGrid.InsertColumn(2, 'Type')
        self.devicesGrid.SetColumnWidth(2, 80)

        self.devicesSizer.Add(self.devicesGrid, 1, flag=wx.EXPAND | wx.ALL, border=20)

        self.devices_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.button_rescan_devices = wx.Button(self, -1, label="Rescan")
        self.devices_buttons_sizer.Add(self.button_rescan_devices, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnRescan, id=self.button_rescan_devices.GetId())
        self.button_rescan_devices.SetToolTip(wx.ToolTip("Replay the device search"))

        button_test_connectivity = wx.Button(self, -1, label="Test")
        self.devices_buttons_sizer.Add(button_test_connectivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnTestDevice, id=button_test_connectivity.GetId())
        button_test_connectivity.SetToolTip(wx.ToolTip("Run a test for the selected device"))

        self.devicesSizer.Add(self.devices_buttons_sizer, 0, flag=wx.CENTER)

        # ----- End of Connected Devices List -----

        # ----- Begin of Start Acquisition Box ----

        start_acquisition_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Acquisition Info'), wx.VERTICAL)
        start_acquisition_sizer.AddSpacer(15)

        bold_font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        selected_items_sizer = wx.FlexGridSizer(cols=2, hgap=15, vgap=10)
        selected_activity_label = wx.StaticText(self, label='Selected activity:')
        self.selected_activity_text = wx.StaticText(self, label='-')
        self.selected_activity_text.SetFont(bold_font)
        selected_device_label = wx.StaticText(self, label='Selected device:')
        self.selected_device_text = wx.StaticText(self, label='-')
        self.selected_device_text.SetFont(bold_font)
        selected_items_sizer.AddMany([selected_activity_label, self.selected_activity_text,
                                      selected_device_label, self.selected_device_text])

        start_acquisition_sizer.Add(selected_items_sizer, proportion=1, flag=wx.LEFT, border=20)
        start_acquisition_sizer.AddSpacer(15)
        self.play_button = wx.Button(self, -1, label='Begin acquisition')
        self.play_button.MinSize = (200, 20)
        self.play_button.SetBackgroundColour("#A7DE9E")
        self.play_button.SetToolTip(wx.ToolTip("Run selected activity and begin acquisition"))
        self.Bind(wx.EVT_BUTTON, self.OnBeginAcquisition, id=self.play_button.GetId())
        start_acquisition_sizer.Add(self.play_button, proportion=1, flag=wx.ALIGN_CENTER)
        start_acquisition_sizer.AddSpacer(15)

        # ----- End of Start Acquisition Box ----

        self.top_sizer.AddSpacer(20)
        self.top_sizer.Add(self.activities_grid_sizer, 1, wx.TOP | wx.EXPAND, border=15)
        self.top_sizer.AddSpacer(20)
        self.top_sizer.Add(self.devicesSizer, 1, wx.TOP | wx.EXPAND, border=15)
        self.top_sizer.AddSpacer(20)

        self.bottom_sizer.AddSpacer(20)
        self.bottom_sizer.Add(external_buttons_sizer, 1, wx.BOTTOM | wx.EXPAND, border=15)
        self.bottom_sizer.AddSpacer(20)
        self.bottom_sizer.Add(start_acquisition_sizer, 1, wx.BOTTOM | wx.EXPAND, border=15)
        self.bottom_sizer.AddSpacer(20)

        self.main_sizer.Add(self.top_sizer, proportion=1, flag=wx.EXPAND)
        self.main_sizer.AddSpacer(20)
        self.main_sizer.Add(self.bottom_sizer, proportion=0, flag=wx.EXPAND)

        self.SetSizer(self.main_sizer)
        self.Show(True)

        if self.controller.conf.scanDevicesOnStartup == "Yes":
            self.refresh_devices_thread = self.refresh_nearby_devices()

        self.test_frame = None
        self.busy_dlg = None
        self.refresh_activities()


    def build_menu(self):
        menu_file = wx.Menu()
        menu_preferences = menu_file.Append(wx.ID_PREFERENCES, "Preferences", "Configuration window")
        menu_exit = menu_file.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
        menu_help = wx.Menu()
        menu_about = menu_help.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menu_advanced = wx.Menu()
        menu_toggle_debug = menu_advanced.Append(-1, "Toggle debug window", "Show or hide a debug window")
        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, "&File")
        menu_bar.Append(menu_help, "&Help")
        menu_bar.Append(menu_advanced, "&Advanced")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.OnClose, menu_exit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menu_about)
        self.Bind(wx.EVT_MENU, self.OnPreferences, menu_preferences)
        self.Bind(wx.EVT_MENU, self.OnToggleDebug, menu_toggle_debug)

        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('D'), menu_toggle_debug.GetId())])
        self.SetAcceleratorTable(accel_tbl)


    def OnSelectActivity(self, _):
        name_col = 1
        selected_row = self.activities_grid.GetFirstSelected()
        name = self.activities_grid.GetItem(selected_row, name_col).GetText()
        if len(name) > 28:
            self.selected_activity_text.SetLabel(name[:28] + "...")
        else:
            self.selected_activity_text.SetLabel(name)

    def OnSelectDevice(self, _):
        name_col = 0
        selected_row = self.devicesGrid.GetFirstSelected()
        name = self.devicesGrid.GetItem(selected_row, name_col).GetText()
        self.selected_device_text.SetLabel(name)

    def OnAddActivity(self, _):
        add_activity_window = AddActivityWindow(self, "Insert activity", control=self.controller)
        add_activity_window.Show()

    def OnEditActivity(self, _):
        if self.is_activity_selected():
            activity_id = self.activities_grid.GetItem(self.activities_grid.GetFirstSelected(), 0).GetText()
            activity = self.controller.get_activity(activity_id)
            types_dict = {"Photo presentation": InsModImageActivity,
                          "Video presentation": InsModVideoActivity,
                          "Sound presentation": InsModSoundActivity,
                          "Associated-Key tagged activity": InsModAssociatedKey,
                          "Manual-defined tagged activity": InsModManualDefined}
            act_type = activity.__class__.name
            edit_activity_window = types_dict[act_type](self, self.controller, activity_id)
            edit_activity_window.Show()
        else:
            InfoDialog("You must select an activity").show()

    def OnRemoveActivity(self, _):
        if self.is_activity_selected():
            activity_id = int(self.activities_grid.GetItem(self.activities_grid.GetFirstSelected(), 0).GetText())
            result = ConfirmDialog("Are you sure to delete that activity?", "Confirm delete operation").get_result()
            if result == wx.ID_YES:
                self.controller.remove_activity(activity_id)
                self.refresh_activities()
                self.selected_activity_text.SetLabel("-")

        else:
            InfoDialog("You must select an activity").show()

    def OnAbout(self, _):
        description = """gVARVI is a free software tool developed to perform heart
rate variability (HRV) analysis in response to different visual stimuli.
The tool was developed after realizing that
this type of studies are becoming popular in fields such as
psychiatry, psychology and marketing, and taking into account
the lack of specific tools for this purpose."""

        licence = """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details."""

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO))
        info.SetName('gVarvi')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014-2015 MileGroup')
        info.SetWebSite('http://milegroup.net/')
        info.SetLicence(licence)
        info.AddDeveloper('Nicolás Vila')
        info.AddDocWriter('Nicolás Vila')

        wx.AboutBox(info)

    def OnClose(self, _):
        result = ConfirmDialog("Quitting VARVI\nAre you sure?", "Confirm exit").get_result()
        if result == wx.ID_YES:
            try:
                self.Destroy()  # Close the frame.
            except AttributeError:
                pass

    def OnPreferences(self, _):
        conf_window = ConfWindow(self, "Preferences", control=self.controller)
        conf_window.Show()

    def OnToggleDebug(self, _):
        if self.debug_window.IsShown():
            self.debug_window.Hide()
            self.Update()
        else:
            self.debug_window.Show()

    def OnRescan(self, _):
        self.selected_device_text.SetLabel("-")
        self.refresh_nearby_devices()

    def OnTestDevice(self, _):
        from bluetooth.btcommon import BluetoothError

        name_col = 0
        mac_col = 1
        type_col = 2

        try:
            if self.is_device_selected():
                selected_row = self.devicesGrid.GetFirstSelected()
                name = self.devicesGrid.GetItem(selected_row, name_col).GetText()
                if name in self.controller.get_supported_devices():
                    mac = self.devicesGrid.GetItem(selected_row, mac_col).GetText()
                    dev_type = self.devicesGrid.GetItem(selected_row, type_col).GetText()
                    self.test_frame = TestDeviceFrame("Running test", self.controller)
                    self.test_frame.run_test(name, mac, dev_type)
                else:
                    ErrorDialog("Device not supported").show()

            else:
                InfoDialog("Please select a device").show()

        except BluetoothError as e:
            if self.test_frame:
                self.test_frame.Destroy()
            err_message = "Bluetooth error\nCODE: {0}".format(e.message)
            ErrorDialog(err_message).show()

    def OnBeginAcquisition(self, _):
        correct_data = True
        dev_name = None
        dev_dir = None
        dev_type = None
        activity_id = None
        mode = None
        if self.is_activity_selected():
            activity_id = self.activities_grid.GetItem(self.activities_grid.GetFirstSelected(), 0).GetText()
            if not self.controller.is_demo_mode() and self.is_device_selected():
                mode = DEVICE_CONNECTED_MODE
                dev_name = self.devicesGrid.GetItem(self.devicesGrid.GetFirstSelected(), 0).GetText()
                dev_dir = self.devicesGrid.GetItem(self.devicesGrid.GetFirstSelected(), 1).GetText()
                dev_type = self.devicesGrid.GetItem(self.devicesGrid.GetFirstSelected(), 2).GetText()

                if dev_name not in self.controller.get_supported_devices():
                    correct_data = False
                    ErrorDialog("Device not supported").show()

            elif self.controller.is_demo_mode():
                mode = DEMO_MODE

            else:
                correct_data = False
                InfoDialog("You must select an activity and a device").show()

        elif self.controller.is_demo_mode():
            correct_data = False
            InfoDialog("You must select an activity").show()

        else:
            correct_data = False
            InfoDialog("You must select an activity and a device").show()

        if correct_data:
            dlg = wx.FileDialog(self, message="Select path and name for this acquisition",
                                defaultDir="",
                                defaultFile="",
                                wildcard="All files(*.*)|*.*",
                                style=wx.FD_SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                try:
                    self.controller.begin_acquisition(path, activity_id, mode, dev_name, dev_type,
                                                      dev_dir, output="text")
                    OnFinishAcquisitionDialog(self, self.controller).Show()

                except MissingFiles:
                    ErrorDialog("Some of activity files has been deleted\nCheck them!").show()
                except AbortedAcquisition:
                    InfoDialog("Activity aborted. Data won't be saved").show()
                except FailedAcquisition:
                    ErrorDialog("Acquisition failed. Data will be saved anyway").show()
                except HostDownError:
                    ErrorDialog("It seems that device is down").show()

    def refresh_nearby_devices(self):
        self.button_rescan_devices.SetLabel("Searching...")
        self.devicesGrid.DeleteAllItems()
        self.devicesGrid.InsertStringItem(0, "  Looking for devices...")
        self.Disable()
        self.Connect(-1, -1, EVT_RESULT_ID, self.OnDeviceSearchFinished)
        return RefreshDevicesThread(self, self.controller)

    def OnDeviceSearchFinished(self, msg):
        data = msg.data
        if isinstance(data, HostDownError):
            ErrorDialog(data.message).show()
        else:
            devices = data
            self.devicesGrid.DeleteAllItems()
            for i, dev in enumerate(devices):
                self.logger.info("Name: {0}\tMAC: {1}".format(dev.name, dev.mac))
                self.devicesGrid.InsertStringItem(i, dev.name)
                self.devicesGrid.SetStringItem(i, 1, dev.mac)
                self.devicesGrid.SetStringItem(i, 2, dev.type)

            number_of_devices = len(devices)

            self.logger.info("Search finished")
            self.show_scan_result(number_of_devices)

        self.button_rescan_devices.Enable()
        self.Disconnect(-1, -1, EVT_RESULT_ID, self.OnDeviceSearchFinished)
        self.button_rescan_devices.SetLabel("Rescan")
        self.Enable()

    def is_activity_selected(self):
        return self.activities_grid.GetFirstSelected() != -1

    def is_device_selected(self):
        return self.devicesGrid.GetFirstSelected() != -1

    def show_scan_result(self, number):
        if number == 0:
            msg = "No device found"
            self.logger.debug(msg)
        else:
            msg = "{0} device(s) found".format(str(number))
            self.logger.debug(msg)
        InfoDialog(msg).show()

    def refresh_activities(self):
        self.activities_grid.DeleteAllItems()
        for i in range(0, len(self.controller.activities)):
            self.activities_grid.InsertStringItem(i, self.controller.activities[i].id)
            self.activities_grid.SetStringItem(i, 1, self.controller.activities[i].name)
            self.activities_grid.SetStringItem(i, 2, self.controller.activities[i].__class__.name)
            i += 1
        self.logger.debug("Activities list updated")


class OnFinishAcquisitionDialog(wx.Frame):
    def __init__(self, parent, controller, *args, **kw):
        super(OnFinishAcquisitionDialog, self).__init__(parent, *args, **kw)
        self.controller = controller
        pnl = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(10)

        main_sizer.AddSpacer(10)
        ok_btn = wx.Button(pnl, label='Do nothing')
        ok_btn.Bind(wx.EVT_BUTTON, self.OnOK)
        main_sizer.Add(ok_btn, 1, wx.ALIGN_CENTER)

        main_sizer.AddSpacer(10)
        ghrv_btn = wx.Button(pnl, label='Open data with gHRV')
        ghrv_btn.Bind(wx.EVT_BUTTON, self.OnGHRV)
        main_sizer.Add(ghrv_btn, 1, wx.ALIGN_CENTER)

        main_sizer.AddSpacer(10)
        plot_btn = wx.Button(pnl, label='Plot results')
        plot_btn.Bind(wx.EVT_BUTTON, self.OnPlotResults)
        main_sizer.Add(plot_btn, 1, wx.ALIGN_CENTER)

        main_sizer.AddSpacer(20)
        pnl.SetSizer(main_sizer)
        self.SetSize((300, 200))
        self.SetTitle('Acquisition finished')
        self.Centre()

    def OnOK(self, _):
        self.Destroy()

    def OnGHRV(self, _):
        sysplat = sys.platform
        if sysplat == "linux2":
            sysexec_ghrv = "/usr/bin/gHRV"
            if os.path.isfile(sysexec_ghrv):
                self.controller.open_ghrv()
                self.Destroy()
            else:
                ErrorDialog("gHRV must be installed in the system").show()
        if sysplat == "win32":
            ErrorDialog("This feature is only available for Linux platforms").show()

    def OnPlotResults(self, _):
        self.controller.plot_results()
        self.Destroy()


class TestDeviceFrame(wx.Frame):
    def __init__(self, title, controller):
        DEFAULT_TITLE_FONT = wx.Font(pointSize=25, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        NORMAL_FONT = wx.Font(pointSize=18, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        self.controller = controller
        self.device = None
        no_close = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=title, size=(400, 260), style=no_close)

        self.SetBackgroundColour(BACKGROUND_COLOUR)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSpacer(20)
        self.status_text = wx.StaticText(self, -1, "Connecting...")
        self.status_text.SetFont(DEFAULT_TITLE_FONT)
        box.Add(self.status_text, 1, wx.ALIGN_CENTER)
        box.AddSpacer(20)

        results_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)
        rr_label = wx.StaticText(self, label='RR Value')
        rr_label.SetFont(NORMAL_FONT)
        self.rr_text = wx.StaticText(self, label='-')
        self.rr_text.SetFont(NORMAL_FONT)
        hr_label = wx.StaticText(self, label='HR Value')
        hr_label.SetFont(NORMAL_FONT)
        self.hr_text = wx.StaticText(self, label='-')
        self.hr_text.SetFont(NORMAL_FONT)

        results_sizer.AddMany([rr_label, self.rr_text,
                               hr_label, self.hr_text])
        box.Add(results_sizer, proportion=1, flag=wx.ALIGN_CENTER)

        box.AddSpacer(20)

        close_button = wx.Button(self, wx.OK, "OK")
        close_button.Bind(wx.EVT_BUTTON, self.OnOk)
        box.Add(close_button, 1, wx.ALIGN_CENTER | wx.CENTER)
        box.AddSpacer(20)
        self.SetSizer(box)
        self.CenterOnScreen()
        self.Show()

    def run_test(self, name, mac, dev_type):
        self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)
        self.device = self.controller.run_test(notify_window=self, name=name, mac=mac, dev_type=dev_type)

    def OnOk(self, _):
        self.Disconnect(-1, -1, EVT_RESULT_ID, self.OnResult)
        if self.device:
            self.controller.end_bt_test(self.device)
        self.Destroy()

    def OnResult(self, event):
        self.status_text.SetLabel("Connected")
        result_dict = event.data
        self.rr_text.SetLabel("{0}".format(result_dict['rr']))
        self.hr_text.SetLabel("{0}".format(result_dict['hr']))


class RefreshDevicesThread(threading.Thread):
    def __init__(self, main_window, controller):
        self.logger = Logger()

        self.main_window = main_window
        self.controller = controller
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        try:
            devices = self.controller.get_nearby_devices()
            PostEvent(self.main_window, ResultEvent(devices))
        except HostDownError as e:
            err_message = e.message
            self.logger.error("{0}".format(err_message))
            PostEvent(self.main_window, ResultEvent(e))
        finally:
            self.main_window.devicesGrid.DeleteAllItems()
            self.main_window.button_rescan_devices.SetLabel("Rescan")
            self.main_window.Enable()



