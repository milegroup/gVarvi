# coding=utf-8
__author__ = 'nico'

import wx
import wx.lib.agw.ultimatelistctrl as ULC

from config import GRID_STYLE, MAIN_ICON
from activities.ManualDefinedActivity import ManualDefinedTag
from activities import ManualDefinedActivity
from view.wxUtils import InfoDialog
from InsModTemplate import InsModTemplate


class InsModManualDefined(InsModTemplate):
    def __init__(self, parent, control, activity_id=-1):
        super(InsModManualDefined, self).__init__(size=(800, 600), parent=parent, control=control,
                                                  insmod_tag_window_type=InsModManualTag, activity_id=activity_id,
                                                  title="New Manual Activity")
        self.Show()

    def refresh_tags(self):
        self.tags_grid.DeleteAllItems()
        for tag in self.tag_ctrl.tags:
            if tag.finish_type == "Timed":
                self.tags_grid.Append(
                    [tag.name, tag.screentext, tag.finish_type, tag.time])
            else:
                self.tags_grid.Append(
                    [tag.name, tag.screentext, tag.finish_type, "-"])

    def build_general_data_sizer(self):
        self.general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        self.name_label = wx.StaticText(self, label='Name')
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))

        if self.modifying:
            self.name_text_ctrl.SetValue(self.activity.name)

        self.general_data_sizer.AddMany([self.name_label, (self.name_text_ctrl, 1, wx.EXPAND)])

        self.general_data_sizer.AddGrowableCol(1, 1)

    def build_tags_grid(self):
        self.tags_grid = ULC.UltimateListCtrl(self, agwStyle=GRID_STYLE)

        self.tags_grid.SetUserLineHeight(30)

        self.tags_grid.InsertColumn(0, 'Name', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(0, 115)
        self.tags_grid.InsertColumn(1, 'Text', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(1, -3)
        self.tags_grid.InsertColumn(2, 'Finish type', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(2, 130)
        self.tags_grid.InsertColumn(3, 'Time', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(3, 70)

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        tags = self.tag_ctrl.tags
        if name == "" or len(tags) == 0:
            correct_data = False
        if correct_data:
            if self.modifying:
                self.controller.update_activity(ManualDefinedActivity, self.activity_id, name, tags)
            else:
                self.controller.add_activity(ManualDefinedActivity, -1, name, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog("Please, don't forget to fill all fields\nAlso remember to add at least one tag").show()


class InsModManualTag(wx.Frame):
    def __init__(self, parent, tag_control, tag_id=-1):
        self.parent = parent
        self.tag_control = tag_control
        self.modifying = tag_id != -1
        self.tag_id = tag_id
        if not self.modifying:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title="New Manual Tag",
                              size=(600, 300))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title="Modifying Manual Tag (id: {0})".format(tag_id),
                              size=(600, 300))
            tag = self.tag_control.tags[self.tag_id]

        self.SetBackgroundColour("#DBE6CC")

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.CenterOnScreen()

        sizer = wx.BoxSizer(wx.VERTICAL)

        general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        name_label = wx.StaticText(self, label='Name')
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))
        screentext_label = wx.StaticText(self, label='Screen Text')
        self.screentext_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))
        finish_type_label = wx.StaticText(self, label='Finish type')
        finish_types = ["Key (SPACE BAR)", "Timed"]
        self.finish_type_ctrl = wx.ComboBox(self, pos=(50, 30), choices=finish_types,
                                            style=wx.CB_READONLY)
        if not self.modifying:
            self.finish_type_ctrl.SetValue("Timed")
        self.finish_type_ctrl.Bind(wx.EVT_COMBOBOX, self.OnSelectFinishType)
        time_label = wx.StaticText(self, label='Time')
        self.time_ctrl = wx.SpinCtrl(self, value='120', min=5, max=1200)
        if self.modifying:
            self.name_text_ctrl.SetValue(tag.name)
            self.screentext_text_ctrl.SetValue(tag.screentext)
            self.finish_type_ctrl.SetValue(tag.finish_type)
            if tag.finish_type == "Timed":
                self.time_ctrl.SetValue(int(tag.time))
            else:
                self.time_ctrl.SetValue(5)
                self.time_ctrl.Disable()

        general_data_sizer.AddMany([name_label, (self.name_text_ctrl, 0, wx.EXPAND),
                                    screentext_label, (self.screentext_text_ctrl, 0, wx.EXPAND),
                                    finish_type_label, (self.finish_type_ctrl, 0, wx.EXPAND),
                                    time_label, self.time_ctrl])

        general_data_sizer.AddGrowableCol(1, 1)

        buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)

        button_save = wx.Button(self, -1, label="Save")
        buttons_sizer.Add(button_save, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=button_save.GetId())
        button_save.SetToolTip(wx.ToolTip("Save the tag"))

        button_cancel = wx.Button(self, -1, label="Cancel")
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip("Return to the main window"))

        sizer.Add(general_data_sizer, 0, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(buttons_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(sizer)

        self.Show()

    def OnSelectFinishType(self, e):
        selected_string = e.GetString()
        if selected_string == "Key (SPACE BAR)":
            self.time_ctrl.Disable()
            self.time_ctrl.SetValue(0)
        else:
            self.time_ctrl.Enable()

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        screentext = self.screentext_text_ctrl.GetValue()
        finish_type = self.finish_type_ctrl.GetValue()
        time = self.time_ctrl.GetValue()
        tag = ManualDefinedTag(name, screentext, finish_type, time)

        if name == "" or screentext == "" or finish_type == "":
            correct_data = False

        if correct_data:
            if self.modifying:
                self.parent.ModifyTag(self.tag_id, tag)
                self.Destroy()
            else:
                self.parent.AddTag(tag)
                self.Destroy()
        else:
            InfoDialog("Please, don't forget to fill all fields with valid data").show()


    def OnCancel(self, e):
        self.Destroy()
