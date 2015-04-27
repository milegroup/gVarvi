# coding=utf-8
__author__ = 'nico'

import time
from wx import PostEvent

from ant.core import event
from ant.core.message import *
from devices.IDevice import IDevice
from facade.ANTManager import ANTManager
from Utils import run_in_thread
from Utils import ResultEvent


class ANTDevice(IDevice):
    def __init__(self):
        self.callback = None
        self.msg = None
        self.ended_adquisition = False
        self.results_writed = False
        self.manager = ANTManager()

    def connect(self, *args):
        self.manager.open_channel()

    def disconnect(self):
        pass

    @run_in_thread
    def run_test(self, notify_window):
        if not self.manager.antnode.evm.running:
            self.manager.antnode.evm.start()
        self.callback = TestCallback(notify_window)
        self.manager.channel.registerCallback(self.callback)

    def finish_test(self):
        self.manager.antnode.evm.removeCallback(self.callback)
        self.manager.antnode.evm.stop()

    @run_in_thread
    def begin_adquisition(self, writer):
        if not self.manager.antnode.evm.running:
            self.manager.antnode.evm.start()
        self.callback = AdquisitionCallback(self, writer)
        self.manager.channel.registerCallback(self.callback)

    def finish_adquisition(self):
        self.manager.antnode.evm.removeCallback(self.callback)
        self.manager.antnode.evm.stop()
        self.ended_adquisition = True


class AdquisitionCallback(event.EventCallback):
    def __init__(self, device, writer):
        self.device = device
        self.writer = writer
        self.hb_count = 0

    def process(self, msg):
        print msg

        if isinstance(msg, ChannelBroadcastDataMessage):
            print "Ended adquisition: {0}".format(self.device.ended_adquisition)
            print "Results writed: {0}".format(self.device.results_writed)
            if self.device.ended_adquisition:
                if not self.device.results_writed:
                    self.writer.close_writer()
                    self.device.results_writed = True
                    return
            else:
                unpacked_message = ANTManager.unpack_broadcast_message(msg)
                print unpacked_message.page_byte
                # Only read page 4
                if "{0:b}".format(unpacked_message.page_byte).endswith("100"):
                    print "Time: {0}".format(time.time())
                    print "Previous: {0}".format(unpacked_message.previous_beat_time)
                    print "Actual: {0}".format(unpacked_message.actual_beat_time)
                    print "self.hb_count = {0}".format(self.hb_count)
                    print "unpacked_message.heartbeat_count = {0}".format(unpacked_message.heartbeat_count)
                    if unpacked_message.heartbeat_count - self.hb_count > 0:
                        rr = (unpacked_message.actual_beat_time - unpacked_message.previous_beat_time) * 1000 / 1024
                        self.hb_count = unpacked_message.heartbeat_count
                        self.writer.write_rr_value(rr)


class TestCallback(event.EventCallback):
    def __init__(self, notify_window):
        self.notify_window = notify_window

    def process(self, msg):
        print msg

        if isinstance(msg, ChannelBroadcastDataMessage):
            unpacked_message = ANTManager.unpack_broadcast_message(msg)
            print "Page byte: ", unpacked_message.page_byte
            # Only read page 4
            if "{0:b}".format(unpacked_message.page_byte).endswith("100"):
                # if unpacked_message.page_byte.endswith("0100"):
                print "Previous beat time: ", unpacked_message.previous_beat_time
                print "Actual beat time: ", unpacked_message.actual_beat_time
                # Times are in 1/1024 units instead of ms
                rr = (unpacked_message.actual_beat_time - unpacked_message.previous_beat_time) * 1000 / 1024
                print "RR interval: ", rr
                test_dict = {'rr': rr}
                print "Heart beat count: ", unpacked_message.heartbeat_count
                print "Computed Heart Rate: ", unpacked_message.computed_heart_rate
                test_dict['hr'] = unpacked_message.computed_heart_rate
                PostEvent(self.notify_window, ResultEvent(test_dict))