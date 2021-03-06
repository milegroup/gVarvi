# coding=utf-8

from wx import PostEvent
import time
import sys
from collections import namedtuple

import usb.core

from third_party.ant.core.node import Node, NetworkKey
from third_party.ant.core.exceptions import DriverError, NodeError
from third_party.ant.core import driver, event
from third_party.ant.core.message import ChannelBroadcastDataMessage, MessageError
from third_party.ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER
from devices.IDevice import IDevice
from utils import run_in_thread
from utils import ResultEvent
from utils import HostDownError
from logger import Logger
from config import ant_SERIAL, ant_NETKEY, ant_lookup_timeout


class ANTDevice(IDevice):
    """
    Class that represents an ANT+ Heart rate monitor.
    """

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
        """
        Connects to ANT+ device by opening a communication channel.
        @param args: List of parameter values (not used).
        """
        self._open_channel()

    def disconnect(self):
        """
        Disconnects ANT+ device.
        """
        pass

    @run_in_thread
    def run_test(self, notify_window):
        """
        Run test for ANT+ device.
        @param notify_window: Window that device will send test data.
        """
        if not self.antnode.evm.running:
            self.antnode.evm.start()
        self.callback = TestCallback(notify_window)
        self.channel.registerCallback(self.callback)

    def finish_test(self):
        """
        Finishes test for ANT+ device.
        """
        self.antnode.evm.removeCallback(self.callback)
        self.antnode.evm.stop()

    def stabilize(self):
        """
        Prevent to retrieve noisy initial data
        """
        pass

    @run_in_thread
    def begin_acquisition(self, writer):
        """
        Starts acquisition by registering custom acquisition callback.
        @param writer: Object that writes acquisition results.
        """
        if not self.antnode.evm.running:
            self.antnode.evm.start()
            self.antnode.evm.callbacks = set()
        self.callback = AcquisitionCallback(self, writer)
        self.channel.registerCallback(self.callback)

    def finish_acquisition(self):
        """
        Finishes acquisition for ANT+ device.
        """
        self.end_acquisition = True
        while not self.ended_acquisition:
            time.sleep(0.1)
        self.antnode.evm.removeCallback(self.callback)
        self.antnode.evm.stop()

    def _open_channel(self, trials=1):
        try:
            self.logger.debug("Trying to open a channel")
            # Initialize driver
            stick = driver.usb2Driver(ant_SERIAL)
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
        """
        Static method that finds nearby ANT+ devices.
        @return: A list of nearby devices.
        """
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
        """
        Finishes devices lookup.
        @param device_found: True if any nearby device has been found.
        """
        ANTDevice.connected = device_found

    @classmethod
    def unpack_broadcast_message(cls, msg):
        """
        Unpack raw message from ANT+ device for make it
        easy-readable.
        @param msg: Raw message from ANT+ device.
        @return: A namedtuple with all necessary parameters.
        """
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
    """
    Custom callback to process an ANT+ message for acquisition.
    @param device: Reference to ANTDevice object.
    @param writer: Object that writes obtained rr values.
    """

    def __init__(self, device, writer):
        self.logger = Logger()

        self.device = device
        self.writer = writer
        self.hb_count = 0
        self.previous_beat_time = -1

    def process(self, msg):
        """
        Does the message processing.
        @param msg: The message
        """
        if isinstance(msg, ChannelBroadcastDataMessage):
            if self.device.end_acquisition:
                if not self.device.results_written:
                    self.writer.close_writer()
                    self.device.results_written = True
                    return
            else:
                unpacked_message = ANTDevice.unpack_broadcast_message(msg)
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
    """
    Custom message to process an ANT+ message for testing a device.
    @param notify_window: Window where testing messages will be sent to.
    """

    def __init__(self, notify_window):
        self.logger = Logger()
        self.notify_window = notify_window

    def process(self, msg):
        """
        Does the message processing.
        @param msg: The message.
        """
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
    """
    Custom callback that process ANT+ device for lookup purposes.
    @param finish_lookup_fn: Function that sets the finish_lookup flag to True.
    """

    def __init__(self, finish_lookup_fn):
        self.finish_lookup_fn = finish_lookup_fn

    def process(self, msg):
        """
        Does the message processing.
        :param msg: The message.
        """
        if isinstance(msg, ChannelBroadcastDataMessage):
            self.finish_lookup_fn(True)