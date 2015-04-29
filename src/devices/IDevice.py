# coding=utf-8
from abc import ABCMeta, abstractmethod
import socket as socketlib
import sys

import bluetooth


__author__ = 'nico'

from Utils import HostDownError


class IDevice:
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, *args):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def run_test(self, notify_window):
        pass

    @abstractmethod
    def finish_test(self):
        pass

    @abstractmethod
    def begin_acquisition(self, writer):
        pass

    @abstractmethod
    def finish_acquisition(self):
        pass


class BTAbstractDevice(IDevice):
    def __init__(self, mac):
        self.mac = mac
        self.socket = None
        self.connected = False

    def connect(self):
        self.socket = bluetooth.BluetoothSocket()
        try:
            self. socket.connect((self.mac, 1))
            self.connected = True
        except bluetooth.BluetoothError as e:
            if e.message[0] == 112:
                raise HostDownError()

    def disconnect(self):
        self.socket.close()
        self.connected = False

    @abstractmethod
    def run_test(self, notify_window):
        pass

    @abstractmethod
    def finish_test(self):
        pass

    @abstractmethod
    def begin_acquisition(self, writer):
        pass

    @abstractmethod
    def finish_acquisition(self):
        pass

    def receive(self, n):
        """
        Receives data from the socket
        :param n: Buffer size in bytes
        :return: Received buffer data
        """
        if sys.platform == "win32":
            return self.socket.recv(n).encode('hex')
        else:
            return self.socket.recv(n, socketlib.MSG_WAITALL).encode('hex')
