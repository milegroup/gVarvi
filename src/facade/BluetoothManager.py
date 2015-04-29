# coding=utf-8
from collections import namedtuple

import bluetooth

from config import bt_lookup_time
from Utils import HostDownError


class BluetoothManager(object):
    @staticmethod
    def get_nearby_devices():
        try:
            plain_list = bluetooth.discover_devices(duration=bt_lookup_time, lookup_names=True)
            device = namedtuple("device", ["name", "type", "mac"])
            devices_dict = [device(name=dev[1], type="BT", mac=dev[0]) for dev in plain_list]
            return devices_dict
        except IOError:
            raise HostDownError()