# coding=utf-8
from abc import abstractmethod

import wx

from utils import get_translation
from view.wxutils import ConfirmDialog, InfoDialog
from config import BACKGROUND_COLOUR, MAIN_ICON


_ = get_translation()

class InsModTemplate(wx.Frame):
    """
    Window template for insert and modify activities.
    @param size: Size of the window, as a tuple (Width, Height). Must be in pixels.
    @param parent: Main frame of application.
    @param main_facade: Facade of the application.
    @param insmod_tag_window_type: Subclass of wx.Frame that performs the insert of modify of a specific tag
    @param activity_id: If the frame is open to modify an activity, this parameter is the id of that activity.
    Otherwise, this parameter gets the value of -1.
    @param title: Frame title..
    """

    def __init__(self, size, parent, main_facade, insmod_tag_window_type, activity_id=-1, title=None):
        self.main_window = parent
        self.main_facade = main_facade
        self.insmod_tag_window_class = insmod_tag_window_type
        self.modifying = activity_id != -1
        self.activity_id = activity_id
        if not self.modifying:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title=title,
                              size=size)
            self.tag_ctrl = TagControl()
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title=_("Modifying Activity (id: {0})").format(activity_id),
                              size=size)
            self.activity = self.main_facade.get_activity(activity_id)
            self.tag_ctrl = TagControl(self.activity.tags)
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        self.CenterOnScreen()

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.general_data_sizer = None
        self.build_general_data_sizer()

        self.tags_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label=_("Tags")), wx.VERTICAL)
        self.tags_grid = None
        self.build_tags_grid()
        if self.modifying:
            self.refresh_tags()
        self.tags_sizer.Add(self.tags_grid, 1, wx.EXPAND | wx.ALL, border=20)

        # Buttons for adding and removing tags

        self.tag_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_tag_bt = wx.Button(self, -1, label=_("Add"))
        self.tag_buttons_sizer.Add(self.add_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnAddTag, id=self.add_tag_bt.GetId())
        self.add_tag_bt.SetToolTip(wx.ToolTip("Add new tag"))

        self.remove_tag_bt = wx.Button(self, -1, label=_("Remove"))
        self.tag_buttons_sizer.Add(self.remove_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveTag, id=self.remove_tag_bt.GetId())
        self.remove_tag_bt.SetToolTip(wx.ToolTip(_("Remove the selected tag")))

        self.edit_tag_bt = wx.Button(self, -1, label=_("Edit"))
        self.tag_buttons_sizer.Add(self.edit_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnEditTag, id=self.edit_tag_bt.GetId())
        self.edit_tag_bt.SetToolTip(wx.ToolTip(_("Rename the selected tag")))

        self.up_tag_bt = wx.Button(self, -1, label=_("Up"))
        self.tag_buttons_sizer.Add(self.up_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnTagUp, id=self.up_tag_bt.GetId())
        self.up_tag_bt.SetToolTip(wx.ToolTip("Up selected tag in the list"))

        self.down_tag_bt = wx.Button(self, -1, label=_("Down"))
        self.tag_buttons_sizer.Add(self.down_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnTagDown, id=self.down_tag_bt.GetId())
        self.down_tag_bt.SetToolTip(wx.ToolTip(_("Down selected tag in the list")))

        self.tags_sizer.Add(self.tag_buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        # Buttons for save or cancel the operation

        self.buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)

        self.button_save = wx.Button(self, -1, label=_("Save"))
        self.buttons_sizer.Add(self.button_save, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=self.button_save.GetId())
        self.button_save.SetToolTip(wx.ToolTip(_("Save the activity")))

        self.button_cancel = wx.Button(self, -1, label=_("Cancel"))
        self.buttons_sizer.Add(self.button_cancel, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=self.button_cancel.GetId())
        self.button_cancel.SetToolTip(wx.ToolTip(_("Return to the main window")))

        self.sizer.Add(self.general_data_sizer, 0, wx.EXPAND | wx.ALL, border=20)
        self.sizer.Add(self.tags_sizer, 1, wx.EXPAND | wx.ALL, border=20)
        self.sizer.Add(self.buttons_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        self.SetSizer(self.sizer)

    @abstractmethod
    def build_general_data_sizer(self):
        pass

    @abstractmethod
    def build_tags_grid(self):
        pass

    @abstractmethod
    def refresh_tags(self):
        pass

    def OnAddTag(self, _):
        self.insmod_tag_window_class(self, self.main_facade)

    def add_tag(self, tag):
        self.tag_ctrl.add_tag(tag)
        self.refresh_tags()

    def modify_tag(self, pos, tag):
        self.tag_ctrl.modify_tag(pos, tag)
        self.refresh_tags()

    def OnRemoveTag(self, _e):
        selected_row = self.tags_grid.GetFirstSelected()
        if selected_row != -1:
            result = ConfirmDialog(_("Are you sure to delete that tag?"), _("Confirm delete operation")).get_result()
            if result == wx.ID_YES:
                self.tag_ctrl.remove_tag(selected_row)
                self.refresh_tags()

        else:
            InfoDialog(_("You must select a tag")).show()

    def OnTagUp(self, _e):
        selected_row = self.tags_grid.GetFirstSelected()
        if selected_row != -1:
            self.tag_ctrl.up_tag(selected_row)
            self.refresh_tags()
            if selected_row > 0:
                self.tags_grid.Select(selected_row - 1)
            else:
                self.tags_grid.Select(0)
        else:
            InfoDialog(_("You must select a tag")).show()

    def OnTagDown(self, _e):
        selected_row = self.tags_grid.GetFirstSelected()
        if selected_row != -1:
            self.tag_ctrl.down_tag(selected_row)
            self.refresh_tags()
            if selected_row < self.tags_grid.GetItemCount() - 1:
                self.tags_grid.Select(selected_row + 1)
            else:
                self.tags_grid.Select(self.tags_grid.GetItemCount() - 1)
        else:
            InfoDialog(_("You must select a tag")).show()

    def OnEditTag(self, _e):
        selected_row = self.tags_grid.GetFirstSelected()
        if selected_row != -1:
            self.insmod_tag_window_class(self, self.tag_ctrl, selected_row)
        else:
            InfoDialog(_("You must select a tag")).show()

    @abstractmethod
    def OnSave(self, _):
        pass

    def OnCancel(self, _):
        self.Destroy()


class TagControl(object):
    def __init__(self, tags=None):
        self.tags = [] if not tags else tags

    def add_tag(self, tag):
        self.tags.append(tag)

    def remove_tag(self, pos):
        self.tags.pop(pos)

    def up_tag(self, pos):
        if pos > 0 and len(self.tags) > 1:
            self.tags[pos], self.tags[pos - 1] = self.tags[pos - 1], self.tags[pos]

    def down_tag(self, pos):
        if len(self.tags) > 1 and pos < len(self.tags) - 1:
            self.tags[pos], self.tags[pos + 1] = self.tags[pos + 1], self.tags[pos]

    def modify_tag(self, pos, tag):
        self.tags[pos] = tag
