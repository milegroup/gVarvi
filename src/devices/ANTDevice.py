# coding=utf-8
__author__ = 'nico'

from wx import PostEvent
import time
import sys
from collections import namedtuple

import usb.core
import usb.util
from ant.core.node import Node, NetworkKey
from ant.core.exceptions import DriverError, NodeError
from ant.core import driver, event
from ant.core.message import ChannelBroadcastDataMessage, MessageError
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER

from devices.IDevice import IDevice
from Utils import run_in_thread
from Utils import ResultEvent
from Utils import HostDownError
from logger import Logger
from config import ant_SERIAL, ant_NETKEY, ant_lookup_timeout


class ANTDevice(IDevice):
    connected = False
    logger = Logger()

    def __init__(self):
        self.logger = Logger()

        self.callback = None
        self.msg = None
        self.end_acquisition = False
        self.ended_acquisition = False
        self.results_written = False

        self.antnode = None
        self.channel = None
        self.callback = None
        self.connected = False

    def connect(self, *args):
        self._open_channel()

    def disconnect(self):
        pass

    @run_in_thread
    def run_test(self, notify_window):
        if not self.antnode.evm.running:
            self.antnode.evm.start()
        self.callback = TestCallback(notify_window)
        self.channel.registerCallback(self.callback)

    def finish_test(self):
        self.antnode.evm.removeCallback(self.callback)
        self.antnode.evm.stop()

    @run_in_thread
    def begin_acquisition(self, writer):
        if not self.antnode.evm.running:
            self.antnode.evm.start()
            self.antnode.evm.callbacks = set()
        self.callback = AcquisitionCallback(self, writer)
        self.channel.registerCallback(self.callback)

    def finish_acquisition(self):
        self.end_acquisition = True
        while not self.ended_acquisition:
            time.sleep(0.1)
        self.antnode.evm.removeCallback(self.callback)
        self.antnode.evm.stop()

    def _open_channel(self, trials=1):
        try:
            self.logger.debug("Trying to open a channel")
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

        except DriverError:
            raise HostDownError("ANT adapter not found")

        except usb.core.USBError:
            if sys.platform != "win32":
                self.logger.warning("Ant adapter is busy. Resetting...")
                self._reset_stick()
                if trials == 2:
                    raise HostDownError("Ant adapter is busy")
                else:
                    trials += 1
                    self._open_channel()
            else:
                raise HostDownError("Ant adapter busy. Please unplug stick and plug it back")

        except NodeError:
            if sys.platform != "win32":
                self.logger.warning("Ant stick timeout. Retrying...")
                self._reset_stick()
                if trials == 2:
                    raise HostDownError("Ant stick timeout. Please unplug stick and plug it back")
                else:
                    trials += 1
                    self._open_channel()
            else:
                raise HostDownError("Ant stick timeout. Please unplug stick and plug it back")

    @classmethod
    def find(cls):
        dev = ANTDevice()
        if dev._is_device_connected():
            device = namedtuple("device", ["name", "type", "mac"])
            return [device(name="ANT+ HR Band", type="ANT+", mac="No mac")]
        else:
            cls.logger.info("Search timeout")
            return []

    def _is_device_connected(self):
        self._open_channel()
        if not self.antnode.evm.running:
            self.antnode.evm.start()
        ANTDevice.connected = False

        self.callback = LookupCallback(self.finish_lookup)
        self.channel.registerCallback(self.callback)

        beg = time.time()
        while not ANTDevice.connected and time.time() - beg < ant_lookup_timeout:
            time.sleep(0.01)

        self.antnode.evm.removeCallback(self.callback)
        self.antnode.evm.stop()
        self._close_channel()

        return ANTDevice.connected

    @staticmethod
    def finish_lookup(device_found):
        ANTDevice.connected = device_found

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

    @staticmethod
    def _reset_stick():
        dev = usb.core.find(idVendor=0x0fcf, idProduct=0x1008)
        dev.reset()

    def _close_channel(self):
        try:
            self.logger.debug("Closing channel")
            self.channel.close()
            self.channel.unassign()
            self.antnode.stop()
        except MessageError:
            if not sys.platform == "win32":
                self._reset_stick()


class AcquisitionCallback(event.EventCallback):
    def __init__(self, device, writer):
        self.logger = Logger()

        self.device = device
        self.writer = writer
        self.hb_count = 0
        self.previous_beat_time = -1

    def process(self, msg):
        print msg

        if isinstance(msg, ChannelBroadcastDataMessage):
            if self.device.end_adquisition:
                if not self.device.results_written:
                    self.writer.close_writer()
                    self.device.results_written = True
                    return
            else:
                unpacked_message = ANTDevice.unpack_broadcast_message(msg)
                print unpacked_message.page_byte
                # Only read page 4
                if "{0:b}".format(unpacked_message.page_byte).endswith("100"):
                    self.logger.debug("Receiving page 4")
                    self.logger.debug("Previous beat time: {0}".format(unpacked_message.previous_beat_time))
                    self.logger.debug("Actual beat time: {0}".format(unpacked_message.actual_beat_time))
                    self.logger.debug("Software heart beat count: {0}".format(self.hb_count))
                    self.logger.debug("Message heart beat count: {0}".format(unpacked_message.heartbeat_count))
                    # If message carries a new beat
                    if unpacked_message.heartbeat_count - self.hb_count > 0:
                        if unpacked_message.heartbeat_count - self.hb_count > 1 and self.previous_beat_time != -1:
                            act = unpacked_message.previous_beat_time
                            prev = self.previous_beat_time
                            if act - prev < 0:
                                rr = (65535 - prev + act) * 1000 / 1024
                            else:
                                rr = (act - prev) * 1000 / 1024
                            self.logger.debug("RR value: {0}".format(rr))
                            self.writer.write_rr_value(rr)
                            self.previous_beat_time = unpacked_message.previous_beat_time
                        if self.previous_beat_time == -1:
                            prev = unpacked_message.previous_beat_time
                        else:
                            prev = self.previous_beat_time
                        act = unpacked_message.actual_beat_time
                        if act - prev < 0:
                            rr = (65535 - prev + act) * 1000 / 1024
                        else:
                            rr = (act - prev) * 1000 / 1024
                        self.logger.debug("RR value: {0}".format(rr))
                        self.previous_beat_time = act
                        self.hb_count = unpacked_message.heartbeat_count
                        self.writer.write_rr_value(rr)
                elif "{0:b}".format(unpacked_message.page_byte).endswith("000"):
                    self.logger.debug("Receiving page 0")


class TestCallback(event.EventCallback):
    def __init__(self, notify_window):
        self.logger = Logger()

        self.notify_window = notify_window

    def process(self, msg):
        print msg

        if isinstance(msg, ChannelBroadcastDataMessage):
            unpacked_message = ANTDevice.unpack_broadcast_message(msg)
            # Only read page 4
            if "{0:b}".format(unpacked_message.page_byte).endswith("100"):
                self.logger.debug("Receiving page 4")
                self.logger.debug("Previous beat time: {0}".format(unpacked_message.previous_beat_time))
                self.logger.debug("Actual beat time: {0}".format(unpacked_message.actual_beat_time))
                # Times are in 1/1024 units instead of ms
                rr = (unpacked_message.actual_beat_time - unpacked_message.previous_beat_time) * 1000 / 1024
                self.logger.debug("RR value: {0}".format(rr))
                test_dict = {'rr': rr}
                self.logger.debug("Heart beat count: {0}".format(unpacked_message.heartbeat_count))
                self.logger.debug("Computed Heart Rate: {0}".format(unpacked_message.computed_heart_rate))
                test_dict['hr'] = unpacked_message.computed_heart_rate
                PostEvent(self.notify_window, ResultEvent(test_dict))


class LookupCallback(event.EventCallback):
    def __init__(self, finish_lookup_fn):
        self.finish_lookup_fn = finish_lookup_fn

    def process(self, msg):
        if isinstance(msg, ChannelBroadcastDataMessage):
            self.finish_lookup_fn(True)