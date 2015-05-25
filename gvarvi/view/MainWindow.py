# -*- coding: utf-8 -*-

import sys
import os
import threading
from wx import PostEvent
import wx.lib.agw.ultimatelistctrl as ULC

from logger import Logger
from ConfWindow import *
from wxutils import InfoDialog, ErrorDialog, ConfirmDialog
from config import ACTIVITIES_LIST_ID, DEVICES_LIST_ID, GRID_STYLE, MAIN_ICON, BACKGROUND_COLOUR
from config import DEVICE_CONNECTED_MODE, DEMO_MODE
from utils import MissingFiles, AbortedAcquisition, FailedAcquisition, HostDownError
from utils import ResultEvent, EVT_RESULT_ID
from view.DebugWindow import DebugWindow
from view.AddActivityWindow import AddActivityWindow
from view.InsModPhotoPresentation import InsModPhotoPresentation
from view.InsModSoundPresentation import InsModSoundPresentation
from view.InsModAssociatedKey import InsModAssociatedKey
from view.InsModManualDefined import InsModManualDefined
from view.InsModVideoPresentation import InsModVideoPresentation
from activities.PhotoPresentation import PhotoPresentation
from activities.SoundPresentation import SoundPresentation
from activities.VideoPresentation import VideoPresentation
from activities.AssociatedKeyActivity import AssociatedKeyActivity
from activities.ManualDefinedActivity import ManualDefinedActivity


class MainWindow(wx.Frame):
    def __init__(self, title, facade):
        self.logger = Logger()

        DEFAULT_TITLE_FONT = wx.Font(pointSize=25, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        self.main_facade = facade

        wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE, title=title, size=(1100, 640))

        self.debug_window = DebugWindow(self)

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        self.CenterOnScreen()

        self.Bind(wx.EVT_CLOSE, self._OnClose)

        self.MinSize = (900, 600)
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("VARVI - MILE Group")

        self._build_menu()

        # ----- Begin of activities box -----

        self.activities_grid_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)

        activities_title = wx.StaticText(self, 0, label="Activities")
        activities_title.SetFont(DEFAULT_TITLE_FONT)
        self.activities_grid_sizer.Add(activities_title, flag=wx.ALIGN_CENTER)
        self.activities_grid = ULC.UltimateListCtrl(self, id=ACTIVITIES_LIST_ID, agwStyle=GRID_STYLE)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnSelectActivity, id=ACTIVITIES_LIST_ID)

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
        self.Bind(wx.EVT_BUTTON, self._OnAddActivity, id=buttonAddActivity.GetId())
        buttonAddActivity.SetToolTip(wx.ToolTip("Add new activity"))

        buttonEditActivity = wx.Button(self, -1, label="Edit")
        self.activities_buttons_sizer.Add(buttonEditActivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnEditActivity, id=buttonEditActivity.GetId())
        buttonEditActivity.SetToolTip(wx.ToolTip("Edit the selected activity"))

        buttonRemoveActivity = wx.Button(self, -1, label="Remove")
        self.activities_buttons_sizer.Add(buttonRemoveActivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnRemoveActivity, id=buttonRemoveActivity.GetId())
        buttonRemoveActivity.SetToolTip(wx.ToolTip("Remove the selected activity"))

        self.activities_grid_sizer.Add(self.activities_buttons_sizer, proportion=0, flag=wx.CENTER)

        # ----- End of activities box -----

        # ----- Begin of control buttons -----

        external_buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        external_buttons_sizer.Add(wx.StaticLine(self, wx.LI_HORIZONTAL), wx.ALIGN_CENTER | wx.BOTTOM, border=50)
        control_buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label="Global options"), wx.HORIZONTAL)

        button_quit = wx.Button(self, -1, label="Quit")
        control_buttons_sizer.Add(button_quit, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnClose, id=button_quit.GetId())
        button_quit.SetToolTip(wx.ToolTip("Click to quit using VARVI"))

        button_about = wx.Button(self, -1, label="About")
        control_buttons_sizer.Add(button_about, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnAbout, id=button_about.GetId())
        button_about.SetToolTip(wx.ToolTip("Click to see information about VARVI"))

        button_config = wx.Button(self, -1, label="Config")
        control_buttons_sizer.Add(button_config, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnPreferences, id=button_config.GetId())
        button_config.SetToolTip(wx.ToolTip("Click to open configuration window"))

        external_buttons_sizer.Add(control_buttons_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM)

        # ----- End of control buttons -----

        # ----- Begin of Connected Devices List -----

        self.devicesSizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)
        connected_devices_title = wx.StaticText(self, 0, "Connected Devices")
        connected_devices_title.SetFont(DEFAULT_TITLE_FONT)
        self.devicesSizer.Add(connected_devices_title, flag=wx.ALIGN_CENTER)
        self.devicesGrid = ULC.UltimateListCtrl(self, id=DEVICES_LIST_ID, agwStyle=GRID_STYLE)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnSelectDevice, id=DEVICES_LIST_ID)

        self.devicesGrid.SetUserLineHeight(30)
        self.devicesGrid.InsertColumn(0, 'Name')
        self.devicesGrid.SetColumnWidth(0, -3)
        self.devicesGrid.InsertColumn(1, 'MAC')
        self.devicesGrid.SetColumnWidth(1, 140)
        self.devicesGrid.InsertColumn(2, 'Type')
        self.devicesGrid.SetColumnWidth(2, 80)

        self.devicesSizer.Add(self.devicesGrid, 1, flag=wx.EXPAND | wx.ALL, border=20)

        self.devices_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.button_rescan_devices = wx.Button(self, -1, label="Scan")
        self.devices_buttons_sizer.Add(self.button_rescan_devices, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnRescan, id=self.button_rescan_devices.GetId())
        self.button_rescan_devices.SetToolTip(wx.ToolTip("Replay the device search"))

        button_test_connectivity = wx.Button(self, -1, label="Test")
        self.devices_buttons_sizer.Add(button_test_connectivity, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self._OnTestDevice, id=button_test_connectivity.GetId())
        button_test_connectivity.SetToolTip(wx.ToolTip("Run a test for the selected device"))

        self.devicesSizer.Add(self.devices_buttons_sizer, 0, flag=wx.CENTER)

        # ----- End of Connected Devices List -----

        # ----- Begin of Start Acquisition Box ----

        start_acquisition_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Acquisition Info'), wx.VERTICAL)
        start_acquisition_sizer.AddSpacer(15)

        bold_font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.NORMAL)
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
        self.Bind(wx.EVT_BUTTON, self._OnBeginAcquisition, id=self.play_button.GetId())
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

        if self.main_facade.conf.scanDevicesOnStartup == "Yes":
            self.refresh_devices_thread = self._refresh_nearby_devices()

        self.test_frame = None
        self.busy_dlg = None
        self.refresh_activities()

        # Mapping between activities and frames that insert and modify each activity
        self.ins_mod_windows = {PhotoPresentation: InsModPhotoPresentation,
                                VideoPresentation: InsModVideoPresentation,
                                SoundPresentation: InsModSoundPresentation,
                                AssociatedKeyActivity: InsModAssociatedKey,
                                ManualDefinedActivity: InsModManualDefined}

    def _build_menu(self):
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
        self.Bind(wx.EVT_MENU, self._OnClose, menu_exit)
        self.Bind(wx.EVT_MENU, self._OnAbout, menu_about)
        self.Bind(wx.EVT_MENU, self._OnPreferences, menu_preferences)
        self.Bind(wx.EVT_MENU, self._OnToggleDebug, menu_toggle_debug)

        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('D'), menu_toggle_debug.GetId())])
        self.SetAcceleratorTable(accel_tbl)

    def _OnSelectActivity(self, _):
        name_col = 1
        selected_row = self.activities_grid.GetFirstSelected()
        name = self.activities_grid.GetItem(selected_row, name_col).GetText()
        if len(name) > 28:
            self.selected_activity_text.SetLabel(name[:28] + "...")
        else:
            self.selected_activity_text.SetLabel(name)

    def _OnSelectDevice(self, _):
        name_col = 0
        selected_row = self.devicesGrid.GetFirstSelected()
        name = self.devicesGrid.GetItem(selected_row, name_col).GetText()
        self.selected_device_text.SetLabel(name)

    def _OnAddActivity(self, _):
        add_activity_window = AddActivityWindow(self, "Insert activity", main_facade=self.main_facade)
        add_activity_window.Show()

    def _OnEditActivity(self, _):
        if self._is_activity_selected():
            activity_id = self.activities_grid.GetItem(self.activities_grid.GetFirstSelected()).GetText()
            activity = self.main_facade.get_activity(activity_id)

            edit_activity_window = self.ins_mod_windows[activity.__class__](self, self.main_facade, activity_id)
            edit_activity_window.Show()
        else:
            InfoDialog("You must select an activity").show()

    def _OnRemoveActivity(self, _):
        if self._is_activity_selected():
            activity_id = int(self.activities_grid.GetItem(self.activities_grid.GetFirstSelected()).GetText())
            result = ConfirmDialog("Are you sure to delete that activity?", "Confirm delete operation").get_result()
            if result == wx.ID_YES:
                self.main_facade.remove_activity(activity_id)
                self.refresh_activities()
                self.selected_activity_text.SetLabel("-")

        else:
            InfoDialog("You must select an activity").show()

    def _OnAbout(self, _):
        description = """gVARVI is a free software tool developed to perform heart
rate variability (HRV) analysis in response to different visual stimuli.
The tool was developed after realizing that
this type of studies are becoming popular in fields such as
psychiatry, psychology and marketing, and taking into account
the lack of specific tools for this purpose."""

        licence = """-------------------------------------------------------------------------
   gVARVI: graphic heart rate Variability Adquisition in Response to audioVisual stImuli
   Copyright (C) 2015  Milegroup - Dpt. Informatics
      University of Vigo - Spain
      www.milegroup.net

   Author:
     - Leandro Rodríguez-Liñares
     - Arturo Méndez
     - María José Lado
     - Xosé Antón Vila
     - Pedro Cuesta Morales

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
-------------------------------------------------------------------------


                              TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

"""

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_PNG))
        info.SetName('gVarvi')
        info.SetVersion('0.1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014-2015 MileGroup')
        info.SetWebSite('http://milegroup.net/')
        info.SetLicence(licence)
        info.AddDeveloper('Leandro Rodríguez-Liñares')
        info.AddDeveloper('Arturo Méndez')
        info.AddDeveloper('María José Lado')
        info.AddDeveloper('Xosé Antón Vila')
        info.AddDeveloper('Pedro Cuesta Morales')
        info.AddDeveloper('Nicolás Vila')
        info.AddDocWriter('Nicolás Vila')

        wx.AboutBox(info)

    def _OnClose(self, _):
        result = ConfirmDialog("Quitting VARVI\nAre you sure?", "Confirm exit").get_result()
        if result == wx.ID_YES:
            try:
                self.Destroy()  # Close the frame.
            except AttributeError:
                pass

    def _OnPreferences(self, _):
        conf_window = ConfWindow(self, main_facade=self.main_facade)
        conf_window.Show()

    def _OnToggleDebug(self, _):
        if self.debug_window.IsShown():
            self.debug_window.Hide()
            self.Update()
        else:
            self.debug_window.Show()

    def _OnRescan(self, _):
        self.selected_device_text.SetLabel("-")
        self._refresh_nearby_devices()

    def _OnTestDevice(self, _):
        from bluetooth.btcommon import BluetoothError

        name_col = 0
        mac_col = 1
        type_col = 2

        try:
            if self._is_device_selected():
                selected_row = self.devicesGrid.GetFirstSelected()
                name = self.devicesGrid.GetItem(selected_row, name_col).GetText()
                if name in self.main_facade.get_supported_devices():
                    mac = self.devicesGrid.GetItem(selected_row, mac_col).GetText()
                    dev_type = self.devicesGrid.GetItem(selected_row, type_col).GetText()
                    self.test_frame = TestDeviceFrame(self.main_facade)
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

    def _OnBeginAcquisition(self, _):
        correct_data = True
        dev_name = None
        dev_dir = None
        dev_type = None
        activity_id = None
        mode = None
        if self._is_activity_selected():
            activity_id = self.activities_grid.GetItem(self.activities_grid.GetFirstSelected()).GetText()
            if not self.main_facade.is_demo_mode() and self._is_device_selected():
                mode = DEVICE_CONNECTED_MODE
                dev_name = self.devicesGrid.GetItem(self.devicesGrid.GetFirstSelected()).GetText()
                dev_dir = self.devicesGrid.GetItem(self.devicesGrid.GetFirstSelected(), 1).GetText()
                dev_type = self.devicesGrid.GetItem(self.devicesGrid.GetFirstSelected(), 2).GetText()

                if dev_name not in self.main_facade.get_supported_devices():
                    correct_data = False
                    ErrorDialog("Device not supported").show()

            elif self.main_facade.is_demo_mode():
                mode = DEMO_MODE

            else:
                correct_data = False
                InfoDialog("You must select an activity and a device").show()

        elif self.main_facade.is_demo_mode():
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

            close_dialog = False
            acquisition = False
            while not close_dialog:
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    if os.path.isfile(path + ".rr.txt") or os.path.isfile(path) or os.path.isfile(path + ".tag.txt"):
                        result = ConfirmDialog("File already exists. Do you want to overwrite it?",
                                               "Confirm").get_result()
                        if result == wx.ID_YES:
                            close_dialog = True
                            acquisition = True
                    else:
                        close_dialog = True
                        acquisition = True
                else:
                    close_dialog = True

            if acquisition:
                try:
                    self.main_facade.begin_acquisition(path, activity_id, mode, dev_name, dev_type,
                                                       dev_dir)
                    OnFinishAcquisitionDialog(self, self.main_facade).Show()

                except MissingFiles:
                    ErrorDialog("Some of activity files has been deleted\nCheck them!").show()
                except AbortedAcquisition:
                    InfoDialog("Activity aborted. Data won't be saved").show()
                except FailedAcquisition:
                    ErrorDialog("Acquisition failed. Data will be saved anyway").show()
                except HostDownError:
                    ErrorDialog("It seems that device is down").show()

    def _refresh_nearby_devices(self):
        self.button_rescan_devices.SetLabel("Searching...")
        self.devicesGrid.DeleteAllItems()
        self.devicesGrid.InsertStringItem(0, "  Looking for devices...")
        self.Disable()
        self.Connect(-1, -1, EVT_RESULT_ID, self._OnDeviceSearchFinished)
        return RefreshDevicesThread(self, self.main_facade)

    def _OnDeviceSearchFinished(self, msg):
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
            self._show_scan_result(number_of_devices)

        self.button_rescan_devices.Enable()
        self.Disconnect(-1, -1, EVT_RESULT_ID, self._OnDeviceSearchFinished)
        self.button_rescan_devices.SetLabel("Scan")
        self.Enable()

    def _is_activity_selected(self):
        return self.activities_grid.GetFirstSelected() != -1

    def _is_device_selected(self):
        return self.devicesGrid.GetFirstSelected() != -1

    def _show_scan_result(self, number):
        if number == 0:
            msg = "No device found"
            self.logger.debug(msg)
        else:
            msg = "{0} device(s) found".format(str(number))
            self.logger.debug(msg)
        InfoDialog(msg).show()

    def refresh_activities(self):
        self.activities_grid.DeleteAllItems()
        for i in range(0, len(self.main_facade.activities)):
            self.activities_grid.InsertStringItem(i, self.main_facade.activities[i].id)
            self.activities_grid.SetStringItem(i, 1, self.main_facade.activities[i].name)
            self.activities_grid.SetStringItem(i, 2, self.main_facade.activities[i].__class__.name)
            i += 1
        self.logger.debug("Activities list updated")


class OnFinishAcquisitionDialog(wx.Frame):
    def __init__(self, parent, main_facade, *args, **kw):
        super(OnFinishAcquisitionDialog, self).__init__(parent, *args, **kw)
        self.main_facade = main_facade
        pnl = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        internal_sizer = wx.BoxSizer(wx.VERTICAL)
        internal_sizer.AddSpacer(20)

        ok_btn = wx.Button(pnl, label='Do nothing')
        ok_btn.Bind(wx.EVT_BUTTON, self._OnOK)
        internal_sizer.Add(ok_btn, 1, wx.EXPAND)

        internal_sizer.AddSpacer(10)
        ghrv_btn = wx.Button(pnl, label='Open in gHRV')
        ghrv_btn.Bind(wx.EVT_BUTTON, self._OnGHRV)
        internal_sizer.Add(ghrv_btn, 1, wx.EXPAND)

        internal_sizer.AddSpacer(10)
        plot_btn = wx.Button(pnl, label='Plot results')
        plot_btn.Bind(wx.EVT_BUTTON, self._OnPlotResults)
        internal_sizer.Add(plot_btn, 1, wx.EXPAND)
        internal_sizer.AddSpacer(20)

        main_sizer.AddSpacer(20)
        main_sizer.Add(internal_sizer, 1, wx.EXPAND)
        main_sizer.AddSpacer(20)

        pnl.SetSizer(main_sizer)
        self.SetSize((300, 200))
        self.SetTitle('Acquisition finished')
        self.Centre()

    def _OnOK(self, _):
        self.Destroy()

    def _OnGHRV(self, _):
        sysplat = sys.platform
        if sysplat == "linux2":
            sysexec_ghrv = "/usr/bin/gHRV"
            if os.path.isfile(sysexec_ghrv):
                self.main_facade.open_ghrv()
                self.Destroy()
            else:
                ErrorDialog("gHRV must be installed in the system").show()
        if sysplat == "win32":
            ErrorDialog("This feature is only available for Linux platforms").show()

    def _OnPlotResults(self, _):
        self.main_facade.plot_results()
        self.Destroy()


class TestDeviceFrame(wx.Frame):
    def __init__(self, main_facade):
        DEFAULT_TITLE_FONT = wx.Font(pointSize=25, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        NORMAL_FONT = wx.Font(pointSize=18, family=wx.SWISS, style=wx.NORMAL, weight=wx.LIGHT)
        self.main_facade = main_facade
        self.device = None
        no_close = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title="Running test", size=(400, 260), style=no_close)

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
        self.device = self.main_facade.run_test(notify_window=self, name=name, mac=mac, dev_type=dev_type)

    def OnOk(self, _):
        self.Disconnect(-1, -1, EVT_RESULT_ID, self.OnResult)
        if self.device:
            self.main_facade.end_device_test(self.device)
        self.Destroy()

    def OnResult(self, event):
        self.status_text.SetLabel("Connected")
        result_dict = event.data
        self.rr_text.SetLabel("{0}".format(result_dict['rr']))
        self.hr_text.SetLabel("{0}".format(result_dict['hr']))


class RefreshDevicesThread(threading.Thread):
    def __init__(self, main_window, main_facade):
        self.logger = Logger()

        self.main_window = main_window
        self.main_facade = main_facade
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        try:
            devices = self.main_facade.get_nearby_devices()
            PostEvent(self.main_window, ResultEvent(devices))
        except HostDownError as e:
            err_message = e.message
            self.logger.error("{0}".format(err_message))
            PostEvent(self.main_window, ResultEvent(e))
        finally:
            self.main_window.devicesGrid.DeleteAllItems()
            self.main_window.button_rescan_devices.SetLabel("Scan")
            self.main_window.Enable()



