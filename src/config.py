# coding=utf-8
__author__ = 'nico'

import os
import wx
import wx.lib.agw.ultimatelistctrl as ULC
from pygame.locals import *

# Paths
PROJECT_PATH = os.path.dirname(__file__)
RESOURCES_FOLDER = os.path.join(PROJECT_PATH, "resources")
DEFAULT_CONF_FILE = os.path.join(RESOURCES_FOLDER, "default.conf.xml")
DEFAULT_ACTIV_FILE = os.path.join(RESOURCES_FOLDER, "default.activ.xml")

CONF_DIR = os.path.expanduser('~') + os.sep + ".gvarvi"
LOG_FILE = os.path.join(CONF_DIR, "gVarvi.log")
CONF_FILE = os.path.join(CONF_DIR, "conf.xml")
ACTIV_FILE = os.path.join(CONF_DIR, "activ.xml")

# Icons
MAIN_ICON = os.path.join(RESOURCES_FOLDER, "heart.ico")
IMAGE_ICON = os.path.join(RESOURCES_FOLDER, "image.png")
VIDEO_ICON = os.path.join(RESOURCES_FOLDER, "video.png")
SOUND_ICON = os.path.join(RESOURCES_FOLDER, "sound.png")
KEY_ICON = os.path.join(RESOURCES_FOLDER, "key.png")
MANUAL_ICON = os.path.join(RESOURCES_FOLDER, "manual.png")

# All players
ABORT_KEY = K_ESCAPE
FINISH_KEY = K_RETURN
NEXT_TAG_KEY = K_SPACE
EXIT_SUCCESS_CODE = 0
EXIT_ABORT_CODE = 1
EXIT_FAIL_CODE = 2

# Posible states at the end of the adquisiton
SUCCESS = 0

ACTIVITY_ABORTED = 1
MISSING_FILES = 2

DEVICE_DOWN = 3

# Audio player
FREQ = 44100  # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2  # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30  # how often to check if playback has finished

# Image player
SUPPORTED_IMG_EXTENSIONS = (".jpg", ".JPG", ".jpeg", "JPEG")

# Bluetooth Test Result Event ID
EVT_RESULT_ID = wx.NewId()

# GUI
BACKGROUND_COLOUR = "#FFFFFF"
ACTIVITIES_LIST_ID = 1
DEVICES_LIST_ID = 2
GRID_STYLE = ULC.ULC_REPORT | ULC.ULC_SINGLE_SEL | ULC.ULC_USER_ROW_HEIGHT | ULC.ULC_HRULES | ULC.ULC_EDIT_LABELS ^ ULC.ULC_EDIT_LABELS

# Adquisiton modes
DEVICE_CONNECTED_MODE = 0
DEMO_MODE = 1

# Pygame to wxPython event mapping
pygame_wx_evt_map = {
    K_0: "0", K_1: "1", K_2: "2", K_3: "3", K_4: "4",
    K_5: "5", K_6: "6", K_7: "7", K_8: "8", K_9: "9",
    K_a: "A", K_b: "B", K_c: "C", K_d: "D", K_e: "E",
    K_f: "F", K_g: "G", K_h: "H", K_i: "I", K_j: "J",
    K_k: "K", K_l: "L", K_m: "M", K_n: "N", K_o: "O",
    K_p: "P", K_q: "Q", K_r: "R", K_s: "S", K_t: "T",
    K_u: "U", K_v: "V", K_w: "W", K_x: "X", K_y: "Y",
    K_z: "Z"
}

# Bluetooth config
bt_lookup_time = 4

# Ant config
ant_lookup_timeout = 5
ant_NETKEY = [0xb9, 0xa5, 0x21, 0xfb, 0xbd, 0x72, 0xc3, 0x45]
ant_SERIAL = '/dev/ttyUSB0'
ant_DEBUG = False
ant_LOG = None


class UserConfig(object):
    """
    Class that represents the user configuration.
    :param config_dict: A dictionary with all parameters and their respective values
    """

    def __init__(self, config_dict):
        for key, value in config_dict.iteritems():
            setattr(self, key, value)