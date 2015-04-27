# coding=utf-8

__author__ = 'nico'

import time
from collections import namedtuple

import usb.core
import usb.util

from ant.core.node import Node, NetworkKey
from ant.core.exceptions import DriverError, NodeError
from ant.core import driver, event
from ant.core.message import ChannelBroadcastDataMessage
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER
from Utils import HostDownError, Singleton
from devices.ProxyDevice import ProxyDevice
from logger import Logger
from config import ant_lookup_timeout, ant_SERIAL, ant_NETKEY


class ANTManager:
    __metaclass__ = Singleton

    def __init__(self):
        self.logger = Logger()
        self.antnode = None
        self.channel = None
        self.callback = None
        self.device_found = False
        self.channel_opened = False

    def open_channel(self):
        if not self.channel_opened:
            try:
                # Initialize driver
                stick = driver.USB2Driver(ant_SERIAL)
                self.antnode = Node(stick)
                self.antnode.start()
                # Setup channel
                key = NetworkKey('N:ANT+', ant_NETKEY)
                self.antnode.setNetworkKey(0, key)
                self.channel = self.antnode.getFreeChannel()
                self.channel.name = 'C:HRM'
                self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
                self.channel.setID(120, 0, 0)
                self.channel.setSearchTimeout(TIMEOUT_NEVER)
                self.channel.setPeriod(8070)
                self.channel.setFrequency(57)
                self.channel.open()
                self.logger.debug("ANT channel opened")
                self.channel_opened = True

            except DriverError:
                raise HostDownError("ANT adapter not found")

            except usb.core.USBError:
                raise HostDownError("ANT adapter busy")

            except NodeError:
                raise HostDownError("Stick connection timeout\nPlease unplug the adapter and plug it back")

        else:
            self.logger.info("Channel already opened")

    def close_channel(self):
        self.channel.close()
        self.channel.unassign()
        self.antnode.stop()

    def get_nearby_devices(self):
        self.open_channel()
        if not self.antnode.evm.running:
            self.antnode.evm.start()
        self.device_found = False
        # Initialize event machine
        self.callback = LookupCallback(self.finish_lookup)
        self.channel.registerCallback(self.callback)

        beg = time.time()
        while not self.device_found and time.time() - beg < ant_lookup_timeout:
            time.sleep(0.01)

        self.antnode.evm.removeCallback(self.callback)
        self.antnode.evm.stop()

        if self.device_found:
            return [ProxyDevice(name="ANT+ HR Band", dev_type="ANT+", mac="No mac")]
        else:
            self.logger.info("Search timeout")
            return []

    def finish_lookup(self, device_found):
        self.device_found = device_found

    @classmethod
    def unpack_broadcast_message(cls, msg):
        message = namedtuple("message",
                             ["page_byte", "previous_beat_time", "actual_beat_time", "heartbeat_count",
                              "computed_heart_rate"])
        page_byte = msg.payload[1]
        byte3 = msg.payload[3]
        byte4 = msg.payload[4]
        previous_beat_time = byte4 << 8 | byte3
        byte5 = msg.payload[5]
        byte6 = msg.payload[6]
        actual_beat_time = byte6 << 8 | byte5
        byte7 = msg.payload[7]
        heartbeat_count = byte7
        computed_heart_rate = msg.payload[8]
        return message(page_byte, previous_beat_time, actual_beat_time, heartbeat_count, computed_heart_rate)


class LookupCallback(event.EventCallback):
    def __init__(self, finish_lookup_fn):
        self.finish_lookup_fn = finish_lookup_fn

    def process(self, msg):
        if isinstance(msg, ChannelBroadcastDataMessage):
            self.finish_lookup_fn(True)




