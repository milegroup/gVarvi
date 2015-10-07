# coding=utf-8

from collections import namedtuple
import socket as socketlib
import sys
from abc import ABCMeta, abstractmethod

import bluetooth

from utils import HostDownError
from config import bt_lookup_time
from devices.IDevice import IDevice
from logger import Logger


class BTDevice(IDevice):
    """
    Abstract class that provides common method implementation.
    to every Bluetooth devices.
    @param mac: Physical address of device.
    """

    __metaclass__ = ABCMeta

    def __init__(self, mac):
        self.mac = mac
        self.socket = None
        self.connected = False
        self.logger = Logger()

    @classmethod
    def find(cls):
        """
        Finds nearby Bluetooth devices.
        @return: A list with every device found.
        @raise HostDownError: If there is no Bluetooth adapter.
        """
        try:
            plain_list = bluetooth.discover_devices(duration=bt_lookup_time, lookup_names=True)
            device = namedtuple("device", ["name", "type", "mac"])
            return [device(name=dev[1], type="BT", mac=dev[0]) for dev in plain_list]
        except IOError:
            raise HostDownError("Bluetooth adapter not found")

    def connect(self):
        """
        Connects to Bluetooth device.
        @raise HostDownError: If connection failed.
        """
        # del self.socket
        #################################################################
        # TODO: En todas as chamadas e este constructor devolve o mesmo obxecto,
        # TODO: e ao chegar ao metodo connect (xusto abaixo) casca
        #################################################################
        self.socket = bluetooth.BluetoothSocket()
        print "Socket id: {0}".format(id(self.socket))
        try:
            self.socket.connect((self.mac, 1))
            self.connected = True
            self.logger.debug("Device connected")
        except bluetooth.BluetoothError as e:
            self.socket.close()
            self.connected = False
            if e.message[0] == 112:
                raise HostDownError("Band connection failed")

    def disconnect(self):
        """
        Disconnects Bluetooth device.
        """
        self.socket.close()
        self.connected = False

    def receive(self, n):
        """
        Receives data from the socket.
        @param n: Buffer size in bytes.
        @return: Received buffer data.
        """
        if sys.platform == "win32":
            return self.socket.recv(n).encode('hex')
        else:
            return self.socket.recv(n, socketlib.MSG_WAITALL).encode('hex')

    # -----------------------------------------------
    # The following methods have to be implemented on
    # each specific subclass

    @abstractmethod
    def run_test(self, notify_window):
        pass

    @abstractmethod
    def finish_test(self):
        pass

    @abstractmethod
    def stabilize(self):
        """
        Prevent to retrieve noisy initial data
        """
        pass

    @abstractmethod
    def begin_acquisition(self, writer):
        pass

    @abstractmethod
    def finish_acquisition(self):
        pass