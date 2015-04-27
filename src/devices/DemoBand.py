# coding=utf-8
__author__ = 'MILE Usuario'

from random import randint
from time import sleep

from devices.IDevice import IDevice
from Utils import run_in_thread


class DemoBand(IDevice):
    def __init__(self):
        self.connected = False
        self.end_test = False
        self.ended_test = False
        self.end_adquisition = False
        self.ended_adquisition = False

    def connect(self, *args):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def run_test(self, notify_window):
        pass

    def finish_test(self):
        pass

    @run_in_thread
    def begin_adquisition(self, writer=None):
        self.end_adquisition = False
        self.ended_adquisition = False
        while not self.end_adquisition:
            waitvalue = randint(800, 900)
            sleep(waitvalue / 1000.0)
            rr = waitvalue
            if writer:
                writer.write_rr_value(rr)
        self.ended_adquisition = True
        if writer:
            writer.close_writer()

    def finish_adquisition(self):
        self.end_adquisition = True



