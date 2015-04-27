# coding=utf-8
__author__ = 'nico'

import wx
import wx.lib.agw.ultimatelistctrl as ULC

from config import GRID_STYLE, MAIN_ICON
from activities.AssociatedKeyActivity import AssociatedKeyTag
from activities import AssociatedKeyActivity
from view.wxUtils import InfoDialog
from InsModTemplate import InsModTemplate


class InsModAssociatedKey(InsModTemplate):
    def __init__(self, parent, control, activity_id=-1):
        super(InsModAssociatedKey, self).__init__(size=(800, 600), parent=parent, control=control,
                                                  insmod_tag_window_type=InsModKeyAssociatedTag,
                                                  activity_id=activity_id,
                                                  title="New Associated-Key Activity")
        self.Show()

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
        self.tags_grid.InsertColumn(2, 'Key code', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(2, 100)

    def refresh_tags(self):
        self.tags_grid.DeleteAllItems()
        for tag in self.tag_ctrl.tags:
            self.tags_grid.Append(
                [tag.name, tag.screentext, tag.key])

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        tags = self.tag_ctrl.tags
        if name == "" or len(tags) == 0:
            correct_data = False
        if correct_data:
            if self.modifying:
                self.controller.update_activity(AssociatedKeyActivity, self.activity_id, name, tags)
            else:
                self.controller.add_activity(AssociatedKeyActivity, -1, name, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog("Please, don't forget to fill all fields\nAlso remember to add at least one tag").show()

    def used_keys(self):
        to_ret = []
        for t in self.tag_ctrl.tags:
            to_ret.append(t.key)
        return to_ret


class InsModKeyAssociatedTag(wx.Frame):
    def __init__(self, parent, tag_control, tag_id=-1):
        self.parent = parent
        self.tag_control = tag_control
        self.modifying = tag_id != -1
        self.tag_id = tag_id
        self.used_keys = self.parent.used_keys()
        self.previous_key = None
        if not self.modifying:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title="New Key Associated Tag",
                              size=(600, 270))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title="Modifying Key Associated Tag (id: {0})".format(tag_id),
                              size=(600, 270))
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
        key_associated_label = wx.StaticText(self, label='Key')
        key_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.key_text_ctrl = wx.TextCtrl(self, -1, size=(350, -1), style=wx.TE_READONLY)
        self.change_key_button = wx.Button(self, -1, label="Change")
        self.Bind(wx.EVT_BUTTON, self.OnChangeKey, id=self.change_key_button.GetId())
        key_sizer.Add(self.key_text_ctrl, 1, wx.EXPAND)
        key_sizer.AddSpacer(20)
        key_sizer.Add(self.change_key_button, 0, wx.RIGHT)
        if self.modifying:
            self.name_text_ctrl.SetValue(tag.name)
            self.screentext_text_ctrl.SetValue(tag.screentext)
            self.key_text_ctrl.SetValue(tag.key)
            self.previous_key = tag.key

        general_data_sizer.AddMany([name_label, (self.name_text_ctrl, 0, wx.EXPAND),
                                    screentext_label, (self.screentext_text_ctrl, 0, wx.EXPAND),
                                    key_associated_label, (key_sizer, 0, wx.EXPAND)])

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

    def OnChangeKey(self, e):
        self.change_key_button.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.change_key_button.SetLabel("Listening...")

    def OnKeyDown(self, e):
        key = e.GetUniChar()
        self.key_text_ctrl.SetValue(unichr(key))
        self.change_key_button.SetLabel("Change")
        self.change_key_button.Unbind(wx.EVT_KEY_DOWN)

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        screentext = self.screentext_text_ctrl.GetValue()
        key = self.key_text_ctrl.GetValue()
        tag = AssociatedKeyTag(name, screentext, key)
        if name == "" or screentext == "" or key == "" or (key in self.used_keys and key != self.previous_key):
            correct_data = False
        else:
            try:
                keystring = str(key)
                if not keystring.isalnum():
                    correct_data = False
            except UnicodeEncodeError:
                correct_data = False

        if correct_data:
            if self.modifying:
                self.parent.ModifyTag(self.tag_id, tag)
                self.Destroy()
            else:
                self.parent.AddTag(tag)
                self.Destroy()
        else:
            InfoDialog(
                """Please, don't forget to fill all fields with valid data
- Every fields are mandatory
- The key must be alphanumeric
- Make you sure that you aren't using this key in
other tag""").show()


    def OnCancel(self, e):
        self.Destroy()
