# coding=utf-8
import os
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from utils import get_translation
from config import GRID_STYLE, MAIN_ICON, BACKGROUND_COLOUR
from activities.ManualDefinedActivity import ManualDefinedTag, ManualDefinedActivity
from view.wxutils import InfoDialog
from InsModTemplate import InsModTemplate

_ = get_translation()

class InsModManualDefined(InsModTemplate):
    """
    Window for insert and modify manual activities.
    @param parent: An instance of InsModTemplate class, that have common methods and parameter for all windows created
    for insert and modify activities.
    @param main_facade: Main facade of application.
    @param activity_id: If the frame is open to modify an activity, this parameter is the id of that activity.
    Otherwise, this parameter gets the value of -1.
    """

    def __init__(self, parent, main_facade, activity_id=-1):
        super(InsModManualDefined, self).__init__(size=(800, 600), parent=parent, main_facade=main_facade,
                                                  insmod_tag_window_type=InsModManualTag, activity_id=activity_id,
                                                  title=_("New Manual Activity"))
        self.Show()

    def refresh_tags(self):
        self.tags_grid.DeleteAllItems()
        for tag in self.tag_ctrl.tags:
            if tag.finish_type == "Timed":
                self.tags_grid.Append(
                    [tag.name, tag.screentext, _("Timed"), tag.time])
            elif tag.finish_type == "Key (SPACE BAR)":
                self.tags_grid.Append(
                    [tag.name, tag.screentext, _("Key (SPACE BAR)"), "-"])

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
        self.tags_grid.InsertColumn(2, _('Finish type'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(2, 130)
        self.tags_grid.InsertColumn(3, _('Time'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(3, 70)

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        tags = self.tag_ctrl.tags
        if name == "" or len(tags) == 0:
            correct_data = False
        if correct_data:
            if self.modifying:
                self.main_facade.update_activity(ManualDefinedActivity, self.activity_id, name, tags)
            else:
                self.main_facade.add_activity(ManualDefinedActivity, -1, name, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog(_("Please, don't forget to fill all fields.{0}Also remember to add at least one "
                         "tag").format(os.linesep)).show()


class InsModManualTag(wx.Frame):
    """
    Window for insert and modify manual activity tags.
    @param parent: An instance of InsModManualDefined that triggered actual frame.
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
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title=_("New Manual Tag"),
                              size=(600, 280))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title=_("Modifying Manual Tag (id: {0})").format(tag_id),
                              size=(600, 280))
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
        finish_type_label = wx.StaticText(self, label=_('Finish type'))
        finish_types = [_("Key (SPACE BAR)"), _("Timed")]
        self.finish_type_ctrl = wx.ComboBox(self, pos=(50, 30), choices=finish_types,
                                            style=wx.CB_READONLY)
        if not self.modifying:
            self.finish_type_ctrl.SetValue(_("Timed"))
        self.finish_type_ctrl.Bind(wx.EVT_COMBOBOX, self._OnSelectFinishType)
        time_label = wx.StaticText(self, label=_('Time'))
        self.time_ctrl = wx.SpinCtrl(self, value='120', min=5, max=1200)
        if self.modifying:
            self.name_text_ctrl.SetValue(tag.name)
            self.screentext_text_ctrl.SetValue(tag.screentext)
            if tag.finish_type == "Timed":
                self.finish_type_ctrl.SetValue(_("Timed"))
            elif tag.finish_type == "Key (SPACE BAR)":
                self.finish_type_ctrl.SetValue(_("Key (SPACE BAR)"))
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

    def _OnSelectFinishType(self, e):
        selected_string = e.GetString()
        if selected_string == _("Key (SPACE BAR)"):
            self.time_ctrl.Disable()
            self.time_ctrl.SetValue(0)
        else:
            self.time_ctrl.Enable()

    def _OnSave(self, _e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        screentext = self.screentext_text_ctrl.GetValue()
        if self.finish_type_ctrl.GetValue() == _("Timed"):
            finish_type = "Timed"
        elif self.finish_type_ctrl.GetValue() == (_("Key (SPACE BAR)")):
            finish_type = "Key (SPACE BAR)"
        time = self.time_ctrl.GetValue()
        tag = ManualDefinedTag(name, screentext, finish_type, time)

        if name == "" or screentext == "" or finish_type == "":
            correct_data = False

        if correct_data:
            if self.modifying:
                self.parent.modify_tag(self.tag_id, tag)
                self.Destroy()
            else:
                self.parent.add_tag(tag)
                self.Destroy()
        else:
            InfoDialog(_("Please, don't forget to fill all fields with valid data")).show()

    def _OnCancel(self, _):
        self.Destroy()
