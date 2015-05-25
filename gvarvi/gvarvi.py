# coding=utf-8
__author__ = 'nico'

import os
from shutil import copyfile
import wx

from config import CONF_DIR, DEFAULT_CONF_FILE, DEFAULT_ACTIV_FILE, CONF_FILE, ACTIV_FILE, LOG_FILE




# Creating necessary files and dirs if not exist
if not os.path.isdir(CONF_DIR):
    os.mkdir(CONF_DIR)
if not os.path.isfile(CONF_FILE):
    copyfile(DEFAULT_CONF_FILE, CONF_FILE)
if not os.path.isfile(ACTIV_FILE):
    copyfile(DEFAULT_ACTIV_FILE, ACTIV_FILE)
if not os.path.isfile(LOG_FILE):
    open(LOG_FILE, 'a').close()

from facade.MainFacade import MainFacade
from view.MainWindow import MainWindow
from logger import Logger


# Application logger initialization
logger = Logger()
logger.debug("Starting app")
main_facade = MainFacade(ACTIV_FILE, CONF_FILE)
conf = main_facade.parse_config_file()
if conf.remoteDebugger == "Yes":
    logger.activate_datagram_logging(conf.rdIP, int(conf.rdPort))

# Application initialization
app = wx.App()
frame = MainWindow("gVARVI", main_facade)
frame.Show()
app.MainLoop()





