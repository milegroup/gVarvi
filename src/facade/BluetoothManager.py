# coding=utf-8
import sys

from devices.ProxyDevice import ProxyDevice
from config import bt_lookup_time
from Utils import HostDownError


try:
    import bluetooth
except ImportError:
    print "   *** ERROR: bluetooth library not installed in the system"
    sys.exit(0)


class BluetoothManager(object):
    def get_nearby_devices(self):
        try:
            plain_list = bluetooth.discover_devices(duration=bt_lookup_time, lookup_names=True)
            devices_dict = [ProxyDevice(name=dev[1], dev_type="BT", mac=dev[0]) for dev in plain_list]
            return devices_dict
        except IOError:
            raise HostDownError()