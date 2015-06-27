# coding=utf-8

import os
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from config import GRID_STYLE, MAIN_ICON, BACKGROUND_COLOUR
from activities.VideoPresentation import VideoTag, VideoPresentation
from view.wxutils import InfoDialog
from InsModTemplate import InsModTemplate


class InsModVideoPresentation(InsModTemplate):
    """
    Window for insert and modify video presentation activities.
    @param parent: An instance of InsModTemplate class, that have common methods and parameter for all windows created
    for insert and modify activities.
    @param main_facade: Main facade of application.
    @param activity_id: If the frame is open to modify an activity, this parameter is the id of that activity.
    Otherwise, this parameter gets the value of -1.
    """

    def __init__(self, parent, main_facade, activity_id=-1):
        super(InsModVideoPresentation, self).__init__(size=(800, 600), parent=parent, main_facade=main_facade,
                                                      insmod_tag_window_type=InsModVideoPresentationTag,
                                                      activity_id=activity_id,
                                                      title="New Video Activity")
        self.Show()

    def refresh_tags(self):
        self.tags_grid.DeleteAllItems()
        for tag in self.tag_ctrl.tags:
            self.tags_grid.Append(
                [tag.name, tag.path])

    def build_general_data_sizer(self):
        self.general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        self.name_label = wx.StaticText(self, label='Name')
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))

        self.random_label = wx.StaticText(self, label='Random')
        self.randomCheckBox = wx.CheckBox(self)

        if self.modifying:
            self.name_text_ctrl.SetValue(self.activity.name)
            if self.activity.random == "Yes":
                self.randomCheckBox.SetValue(True)
            else:
                self.randomCheckBox.SetValue(False)

        self.general_data_sizer.AddMany([self.name_label, (self.name_text_ctrl, 1, wx.EXPAND),
                                         self.random_label, self.randomCheckBox])

        self.general_data_sizer.AddGrowableCol(1, 1)

    def build_tags_grid(self):
        self.tags_grid = ULC.UltimateListCtrl(self, agwStyle=GRID_STYLE)

        self.tags_grid.SetUserLineHeight(30)

        self.tags_grid.InsertColumn(0, 'Name', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(0, 115)
        self.tags_grid.InsertColumn(1, 'Path', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(1, -3)

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        if self.randomCheckBox.IsChecked():
            random = "Yes"
        else:
            random = "No"
        tags = self.tag_ctrl.tags
        if name == "" or len(tags) == 0:
            correct_data = False
        if correct_data:
            if self.modifying:
                self.main_facade.update_activity(VideoPresentation, self.activity_id, name, random, tags)
            else:
                self.main_facade.add_activity(VideoPresentation, -1, name, random, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog("Please, don't forget to fill all fields" + os.linesep + "Also remember to add at least one " \
                                                                                "tag").show()


class InsModVideoPresentationTag(wx.Frame):
    """
    Window for insert and modify video presentation tags.
    @param parent: An instance of InsModVideoPresentation that triggered actual frame.
    @param tag_control: Object that controls all operations in tag list (insertions, deletions and updates).
    @param tag_id: If the frame is open to modify a tag, this parameter is the id of that tag.
    Otherwise, this parameter gets the value of -1.
    """

    def __init__(self, parent, tag_control, tag_id=-1):
        self.parent = parent
        self.tag_control = tag_control
        self.modifying = tag_id != -1
        self.tag_id = tag_id
        if not self.modifying:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title="New Video Tag",
                              size=(600, 250))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title="Modifying Video Tag (id: {0})".format(tag_id),
                              size=(600, 250))
            tag = self.tag_control.tags[self.tag_id]

        self.SetBackgroundColour(BACKGROUND_COLOUR)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        self.CenterOnScreen()

        sizer = wx.BoxSizer(wx.VERTICAL)

        general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        name_label = wx.StaticText(self, label='Name')
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))
        if self.modifying:
            self.name_text_ctrl.SetValue(tag.name)

        path_label = wx.StaticText(self, label='Path')
        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.path_text_ctrl = wx.TextCtrl(self, -1, size=(350, -1))
        if self.modifying:
            self.path_text_ctrl.SetValue(tag.path)
        self.path_button = wx.Button(self, -1, label="...")
        self.Bind(wx.EVT_BUTTON, self._OnChangePath, id=self.path_button.GetId())
        self.path_button.SetMinSize((40, 25))
        path_sizer.Add(self.path_text_ctrl, 1, wx.EXPAND)
        path_sizer.AddSpacer(20)
        path_sizer.Add(self.path_button, 0, wx.RIGHT)

        general_data_sizer.AddMany([name_label, (self.name_text_ctrl, 0, wx.EXPAND),
                                    path_label, (path_sizer, 0, wx.EXPAND)])

        general_data_sizer.AddGrowableCol(1, 1)

        buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)

        button_save = wx.Button(self, -1, label="Save")
        buttons_sizer.Add(button_save, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnSave, id=button_save.GetId())
        button_save.SetToolTip(wx.ToolTip("Save the tag"))

        button_cancel = wx.Button(self, -1, label="Cancel")
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip("Return to the main window"))

        sizer.Add(general_data_sizer, 0, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(buttons_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        self.SetSizer(sizer)

        self.Show()

    def _OnChangePath(self, _):

        wildcard = "Video source (*.mpg)|*.mpg"

        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.path_text_ctrl.SetValue(path)
        dlg.Destroy()

    def _OnSave(self, _):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        path = self.path_text_ctrl.GetValue()
        tag = VideoTag(name, path)

        if name == "" or path == "" or not os.path.isfile(path):
            correct_data = False

        if correct_data:
            if self.modifying:
                self.parent.modify_tag(self.tag_id, tag)
                self.Destroy()
            else:
                self.parent.add_tag(tag)
                self.Destroy()
        else:
            InfoDialog("Please, don't forget to fill all fields with valid data").show()

    def _OnCancel(self, _):
        self.Destroy()
