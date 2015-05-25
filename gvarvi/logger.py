# coding=utf-8
__author__ = 'nico'

import logging
import logging.handlers

from config import LOG_FILE
from utils import Singleton


class Logger(logging.Logger):
    """
    Custom class for send debug messages to console (standard output), file (log) and net (datagram socket)
    """
    __metaclass__ = Singleton

    def __init__(self):
        logging.Logger.__init__(self, name="logger", level=logging.DEBUG)

        # Formatters
        self.to_file_formatter = logging.Formatter(
            "%(levelname)s %(asctime)s Func: %(funcName)s Line:%(lineno)d -- %(message)s")
        self.to_console_formatter = logging.Formatter("%(levelname)s -- %(message)s")
        self.to_datagram_formatter = logging.Formatter("%(message)s")

        # Handlers
        self.file_handler = logging.FileHandler(filename=LOG_FILE)
        self.file_handler.setFormatter(self.to_file_formatter)
        self.file_handler.setLevel(logging.DEBUG)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.to_console_formatter)
        self.console_handler.setLevel(logging.DEBUG)
        self.datagram_handler = logging.handlers.DatagramHandler("10.10.10.10", 8888)
        self.datagram_handler.setFormatter(self.to_datagram_formatter)
        self.datagram_handler.setLevel(logging.DEBUG)

        # Activation of console and file handlers
        self.addHandler(self.file_handler)
        self.addHandler(self.console_handler)

    def activate_datagram_logging(self, ip, port):
        """
        Activates remote debugging system.
        @param ip: ip of remote debugger.
        @param port: port of remote debugger.
        """
        self.datagram_handler.host = ip
        self.datagram_handler.port = port
        self.addHandler(self.datagram_handler)

    def deactivate_datagram_logging(self):
        """
        Deactivates remote debugging system.
        """
        if self.datagram_handler in self.handlers:
            self.removeHandler(self.datagram_handler)
