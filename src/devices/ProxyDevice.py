# coding=utf-8
__author__ = 'nico'


class ProxyDevice(object):
    """
    Proxy of a device with no logic, only for display device info on GUI
    :param name: name of the device
    :param mac: MAC direction, for Blutooth devices
    """

    def __init__(self, name, dev_type, mac=None):
        self.name = name
        self.mac = mac
        self.type = dev_type