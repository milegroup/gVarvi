# coding=utf-8

import os
from shutil import copyfile
import wx
import sys
import traceback

from config import CONF_DIR, DEFAULT_CONF_FILE, DEFAULT_ACTIV_FILE, CONF_FILE, ACTIV_FILE, LOG_FILE
from utils import set_language


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
from logger import Logger

# Application logger initialization
logger = Logger()
main_facade = MainFacade(ACTIV_FILE, CONF_FILE)
conf = main_facade.parse_config_file()
if conf.remoteDebugger == "Yes":
    logger.activate_datagram_logging(conf.rdIP, int(conf.rdPort))

set_language(conf.language)

class GVarviApp(wx.App):
    def OnInit(self):
        def exception_hook(exc_type, value, trace):
            """
            Handler for all unhandled exceptions
            @param exc_type: Exception type
            @param value: Error value
            @param trace: Trace back info
            """

            # Format the traceback
            exc = traceback.format_exception(exc_type, value, trace)
            ftrace = "".join(exc)
            app = wx.GetApp()
            if app:
                msg = "An unexpected error has ocurred: {0}".format(ftrace)
                logger.exception(msg)
            else:
                sys.stderr.write(ftrace)

        logger.debug("Starting app")
        sys.excepthook = exception_hook

        return True

# Application initialization
from view.MainWindow import MainWindow

app = GVarviApp()
frame = MainWindow("gVARVI", main_facade)
frame.Show()
app.MainLoop()
