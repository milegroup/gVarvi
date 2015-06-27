# coding=utf-8
import os
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from utils import get_translation
from config import GRID_STYLE, MAIN_ICON, BACKGROUND_COLOUR
from activities.AssociatedKeyActivity import AssociatedKeyTag, AssociatedKeyActivity
from view.wxutils import InfoDialog
from InsModTemplate import InsModTemplate

_ = get_translation()

class InsModAssociatedKey(InsModTemplate):
    """
    Window for insert and modify associated-key tagged activities.
    @param parent: An instance of InsModTemplate class, that have common methods and parameter for all windows created
    for insert and modify activities.
    @param main_facade: Main facade of application.
    @param activity_id: If the frame is open to modify an activity, this parameter is the id of that activity.
    Otherwise, this parameter gets the value of -1.
    """

    def __init__(self, parent, main_facade, activity_id=-1):
        super(InsModAssociatedKey, self).__init__(size=(800, 600), parent=parent, main_facade=main_facade,
                                                  insmod_tag_window_type=InsModAssociatedKeyTag,
                                                  activity_id=activity_id,
                                                  title=_("New Associated-Key Activity"))
        self.Show()

    def build_general_data_sizer(self):
        self.general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        self.name_label = wx.StaticText(self, label=_('Name'))
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))

        if self.modifying:
            self.name_text_ctrl.SetValue(self.activity.name)

        self.general_data_sizer.AddMany([self.name_label, (self.name_text_ctrl, 1, wx.EXPAND)])

        self.general_data_sizer.AddGrowableCol(1, 1)

    def build_tags_grid(self):
        self.tags_grid = ULC.UltimateListCtrl(self, agwStyle=GRID_STYLE)

        self.tags_grid.SetUserLineHeight(30)

        self.tags_grid.InsertColumn(0, _('Name'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(0, 115)
        self.tags_grid.InsertColumn(1, _('Text'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(1, -3)
        self.tags_grid.InsertColumn(2, _('Key code'), ULC.ULC_FORMAT_CENTER)
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
                self.main_facade.update_activity(AssociatedKeyActivity, self.activity_id, name, tags)
            else:
                self.main_facade.add_activity(AssociatedKeyActivity, -1, name, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog(_("Please, don't forget to fill all fields.{0}Also remember to add at least one tag").format(
                os.linesep)).show()

    def used_keys(self):
        return [t.key for t in self.tag_ctrl.tags]


class InsModAssociatedKeyTag(wx.Frame):
    """
    Window for insert and modify associated key tags.
    @param parent: An instance of InsModAssociatedKey that triggered actual frame.
    @param tag_control: Object that controls all operations in tag list (insertions, deletions and updates).
    @param tag_id: If the frame is open to modify a tag, this parameter is the id of that tag.
    Otherwise, this parameter gets the value of -1.
    """

    def __init__(self, parent, tag_control, tag_id=-1):
        self.parent = parent
        self.tag_control = tag_control
        self.modifying = tag_id != -1
        self.tag_id = tag_id
        self.used_keys = self.parent.used_keys()
        self.previous_key = None
        if not self.modifying:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title=_("New Associated Key Tag"),
                              size=(600, 245))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title=_("Modifying Associated Key Tag (id: {0})").format(tag_id),
                              size=(600, 245))
            tag = self.tag_control.tags[self.tag_id]

        self.SetBackgroundColour(BACKGROUND_COLOUR)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        self.CenterOnScreen()

        sizer = wx.BoxSizer(wx.VERTICAL)

        general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        name_label = wx.StaticText(self, label=_('Name'))
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))
        screentext_label = wx.StaticText(self, label=_('Screen Text'))
        self.screentext_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))
        key_associated_label = wx.StaticText(self, label=_('Key'))
        key_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.key_text_ctrl = wx.TextCtrl(self, -1, size=(350, -1), style=wx.TE_READONLY)
        self.change_key_button = wx.Button(self, -1, label=_("Change"))
        self.Bind(wx.EVT_BUTTON, self._OnChangeKey, id=self.change_key_button.GetId())
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

        button_save = wx.Button(self, -1, label=_("Save"))
        buttons_sizer.Add(button_save, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnSave, id=button_save.GetId())
        button_save.SetToolTip(wx.ToolTip(_("Save the tag")))

        button_cancel = wx.Button(self, -1, label=_("Cancel"))
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip(_("Return to the main window")))

        sizer.Add(general_data_sizer, 0, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(buttons_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(sizer)

        self.Show()

    def _OnChangeKey(self, _e):
        self.change_key_button.Bind(wx.EVT_KEY_DOWN, self._OnKeyDown)
        self.change_key_button.SetLabel(_("Listening..."))

    def _OnKeyDown(self, e):
        key = e.GetUniChar()
        self.key_text_ctrl.SetValue(unichr(key))
        self.change_key_button.SetLabel(_("Change"))
        self.change_key_button.Unbind(wx.EVT_KEY_DOWN)

    def _OnSave(self, _e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        screentext = self.screentext_text_ctrl.GetValue()
        key = self.key_text_ctrl.GetValue()
        tag = AssociatedKeyTag(name, screentext, key)
        if screentext == "" or key == "" or (
                        key in self.used_keys and key != self.previous_key):
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
                self.parent.modify_tag(self.tag_id, tag)
                self.Destroy()
            else:
                self.parent.add_tag(tag)
                self.Destroy()
        else:
            InfoDialog(
                _("""Please, don't forget to fill all fields with valid data
- Every fields are mandatory
- The key must be alphanumeric
- Make you sure that you aren't using this key in
other tag""")).show()

    def _OnCancel(self, _):
        self.Destroy()
