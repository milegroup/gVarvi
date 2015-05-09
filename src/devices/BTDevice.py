# coding=utf-8

from abc import abstractmethod
import bluetooth
from collections import namedtuple
import socket as socketlib
import sys

from Utils import HostDownError
from config import bt_lookup_time
from devices.IDevice import IDevice


__author__ = 'nico'


class BTDevice(IDevice):
    def __init__(self, mac):
        self.mac = mac
        self.socket = None
        self.connected = False

    @classmethod
    def find(cls):
        try:
            plain_list = bluetooth.discover_devices(duration=bt_lookup_time, lookup_names=True)
            device = namedtuple("device", ["name", "type", "mac"])
            devices_dict = [device(name=dev[1], type="BT", mac=dev[0]) for dev in plain_list]
            return devices_dict
        except IOError:
            raise HostDownError()

    def connect(self):
        self.socket = bluetooth.BluetoothSocket()
        try:
            self.socket.connect((self.mac, 1))
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