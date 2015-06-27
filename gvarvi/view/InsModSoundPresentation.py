# coding=utf-8

import os
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from utils import get_translation
from config import MAIN_ICON, BACKGROUND_COLOUR
from activities.SoundPresentation import SoundPresentation, SoundPresentationTag, Image
from view.wxutils import InfoDialog
from InsModTemplate import InsModTemplate

_ = get_translation()

class InsModSoundPresentation(InsModTemplate):
    """
    Window for insert and modify sound presentation activities.
    @param parent: An instance of InsModTemplate class, that have common methods and parameter for all windows created
    for insert and modify activities.
    @param main_facade: Main facade of application.
    @param activity_id: If the frame is open to modify an activity, this parameter is the id of that activity.
    Otherwise, this parameter gets the value of -1.
    """

    def __init__(self, parent, main_facade, activity_id=-1):
        super(InsModSoundPresentation, self).__init__(size=(800, 600), parent=parent, main_facade=main_facade,
                                                      insmod_tag_window_type=InsModSoundPresentationTag,
                                                      activity_id=activity_id,
                                                      title=_("New Sound Activity"))
        self.Show()

    def refresh_tags(self):
        self.tags_grid.DeleteAllItems()
        for tag in self.tag_ctrl.tags:
            if tag.images:
                self.tags_grid.Append(
                    [tag.name, tag.path, tag.associated_image,
                     ";".join([image.path for image in tag.images])])
            else:
                self.tags_grid.Append(
                    [tag.name, tag.path, tag.associated_image, ""])

    def build_general_data_sizer(self):
        self.general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        self.name_label = wx.StaticText(self, label=_('Name'))
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))

        self.random_label = wx.StaticText(self, label=_('Random'))
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
        self.tags_grid = ULC.UltimateListCtrl(self,
                                              agwStyle=ULC.ULC_REPORT | ULC.ULC_SINGLE_SEL | ULC.ULC_USER_ROW_HEIGHT | ULC.ULC_HRULES | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

        self.tags_grid.SetUserLineHeight(30)

        self.tags_grid.InsertColumn(0, _('Name'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(0, 115)
        self.tags_grid.InsertColumn(1, _('Path'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(1, 200)
        self.tags_grid.InsertColumn(2, _('Associated image'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(2, 140)
        self.tags_grid.InsertColumn(3, _('Images'), ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(3, -3)

    def OnSave(self, _e):
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
                self.main_facade.update_activity(SoundPresentation, self.activity_id, name, random, tags)
            else:
                self.main_facade.add_activity(SoundPresentation, -1, name, random, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog(_("Please, don't forget to fill all fields.{0}Also remember to add at least one "
                         "tag").format(os.linesep)).show()


class InsModSoundPresentationTag(wx.Frame):
    """
    Window for insert and modify sound presentation tags.
    @param parent: An instance of InsModSoundPresentation that triggered actual frame.
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
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title=_("New Sound Tag"),
                              size=(600, 600))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title=_("Modifying Sound Tag (id: {0})").format(tag_id),
                              size=(600, 600))
            tag = self.tag_control.tags[self.tag_id]

        self.SetBackgroundColour(BACKGROUND_COLOUR)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        self.CenterOnScreen()

        sizer = wx.BoxSizer(wx.VERTICAL)

        general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        name_label = wx.StaticText(self, label=_('Name'))
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))
        if self.modifying:
            self.name_text_ctrl.SetValue(tag.name)

        path_label = wx.StaticText(self, label=_('Path'))
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

        associated_image_label = wx.StaticText(self, label=_('Associated image'))
        self.associated_image_checkbox = wx.CheckBox(self)
        if self.modifying and tag.associated_image == "Yes":
            self.associated_image_checkbox.SetValue(True)

        random_label = wx.StaticText(self, label=_('Randomize images'))
        self.random_checkbox = wx.CheckBox(self)
        if self.modifying and tag.random == "Yes":
            self.random_checkbox.SetValue(True)

        general_data_sizer.AddMany([name_label, (self.name_text_ctrl, 0, wx.EXPAND),
                                    path_label, (path_sizer, 0, wx.EXPAND),
                                    associated_image_label, self.associated_image_checkbox,
                                    random_label, self.random_checkbox])

        general_data_sizer.AddGrowableCol(1, 1)

        images_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label=_("Images")), wx.VERTICAL)

        self.images_listbox = wx.ListBox(self, -1)
        if self.modifying and len(tag.images) != 0:
            for image in tag.images:
                self.images_listbox.Append(image.path)

        images_sizer.Add(self.images_listbox, 1, wx.EXPAND | wx.ALL, border=20)

        tag_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons for adding and removing tags

        add_tag_bt = wx.Button(self, -1, label=_("Add"))
        tag_buttons_sizer.Add(add_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self._OnAddImage, id=add_tag_bt.GetId())
        add_tag_bt.SetToolTip(wx.ToolTip(_("Add new tag")))

        remove_tag_bt = wx.Button(self, -1, label=_("Remove"))
        tag_buttons_sizer.Add(remove_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self._OnRemoveImage, id=remove_tag_bt.GetId())
        remove_tag_bt.SetToolTip(wx.ToolTip(_("Remove the selected tag")))

        up_tag_bt = wx.Button(self, -1, label=_("Up"))
        tag_buttons_sizer.Add(up_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self._OnImageUp, id=up_tag_bt.GetId())
        up_tag_bt.SetToolTip(wx.ToolTip(_("Up selected tag in the list")))

        down_tag_bt = wx.Button(self, -1, label=_("Down"))
        tag_buttons_sizer.Add(down_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self._OnImageDown, id=down_tag_bt.GetId())
        down_tag_bt.SetToolTip(wx.ToolTip(_("Down selected tag in the list")))

        images_sizer.Add(tag_buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)

        button_save = wx.Button(self, -1, label=_("Save"))
        buttons_sizer.Add(button_save, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnSave, id=button_save.GetId())
        button_save.SetToolTip(wx.ToolTip(_("Save the activity")))

        button_cancel = wx.Button(self, -1, label=_("Cancel"))
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip(_("Return to the main window")))

        sizer.Add(general_data_sizer, 0, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(images_sizer, 1, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(buttons_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        self.SetSizer(sizer)

        self.Show()

    def _OnChangePath(self, _e):

        wildcard = "Audio source (*.mp3; *wav)|*.mp3;*.wav"

        dlg = wx.FileDialog(
            self, message=_("Choose a file"),
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.path_text_ctrl.SetValue(path)
        dlg.Destroy()

    def _OnAddImage(self, _e):
        wildcard = "Image source (*.jpg; *.jpeg; *.png; *.bmp; *.tif; *.xpm; " \
                   "*.pcx)|*.jpg;*.JPG;*.jpeg;*.JPEG;*.png;*.PNG;*.bmp;*.BMP;*.tif;*.TIF;*.xmp;*.XPM;*.pcx;*.PCX"

        dlg = wx.FileDialog(
            self, message=_("Choose a file"),
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                self.images_listbox.Append(path)
        dlg.Destroy()

    def _OnRemoveImage(self, _):
        sel = self.images_listbox.GetSelection()
        if sel != -1:
            self.images_listbox.Delete(sel)

    def _OnImageUp(self, _):
        sel_pos = self.images_listbox.GetSelection()
        if sel_pos > 0:
            sel_path = self.images_listbox.GetStringSelection()
            self.images_listbox.Delete(sel_pos)
            self.images_listbox.Insert(sel_path, sel_pos - 1)

    def _OnImageDown(self, _):
        sel_pos = self.images_listbox.GetSelection()
        if sel_pos < self.images_listbox.GetCount() - 1 and sel_pos != -1:
            sel_path = self.images_listbox.GetStringSelection()
            self.images_listbox.Delete(sel_pos)
            self.images_listbox.Insert(sel_path, sel_pos + 1)

    def _OnSave(self, _e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        path = self.path_text_ctrl.GetValue()
        if self.random_checkbox.IsChecked():
            random = "Yes"
        else:
            random = "No"
        if self.associated_image_checkbox.IsChecked():
            associated_image = "Yes"
        else:
            associated_image = "No"
        images = [Image(image_path) for image_path in self.images_listbox.GetItems()]
        tag = SoundPresentationTag(name, path, random, associated_image, images)

        if name == "" or path == "" or not os.path.isfile(path):
            correct_data = False

        if associated_image == "Yes" and len(images) == 0:
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

    def OnCancel(self, _):
        self.Destroy()
