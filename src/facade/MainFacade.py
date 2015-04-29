# coding=utf-8
__author__ = 'nico'

import os

from dao.XMLMapper import XMLMapper
from BluetoothManager import *
from ANTManager import *
from Utils import Singleton
from facade.AcquisitionFacade import AcquisitionFacade
from devices.PolariWL import PolariWL
from devices.DemoBand import DemoBand
from devices.ANTDevice import ANTDevice
from facade.Writer import TextWriter
from config import DEVICE_CONNECTED_MODE, DEMO_MODE
from Utils import run_in_thread
from logger import Logger
from facade.Painter import paint


class MainFacade:
    __metaclass__ = Singleton

    def __init__(self, activ_file, conf_file):
        self.logger = Logger()

        self.actFilePath = activ_file
        self.confFilePath = conf_file
        self.xmlMapper = XMLMapper(self.actFilePath, self.confFilePath)
        self.activities = self.parse_activities_file()
        self.btMgr = BluetoothManager()
        self.antMgr = ANTManager()
        self.valid_devices = ["Polar iWL", "ANT+ HR Band"]
        self.conf = None
        self.test_thread = None
        self.acquisition_path = None

    def activate_remote_debug(self, ip, port):
        self.logger.activate_datagram_logging(ip, port)

    def deactivate_remote_debug(self):
        self.logger.deactivate_datagram_logging()

    def parse_activities_file(self):
        activities = self.xmlMapper.read_activities_file()
        return activities

    def refresh_activities(self):
        self.activities = self.parse_activities_file()

    def parse_config_file(self):
        conf = self.xmlMapper.read_config_file()
        self.conf = conf
        return conf

    def reset_config(self):
        self.xmlMapper.reset_config()
        self.parse_config_file()

    def save_config(self):
        self.xmlMapper.save_config(self.conf.__dict__)

    def get_activity(self, activity_id):
        return self.xmlMapper.get_activity(activity_id)

    def add_activity(self, activity_class, *args, **kwargs):
        activity = activity_class(*args, **kwargs)
        self.xmlMapper.save_activity(activity)
        self.refresh_activities()

    def update_activity(self, activity_class, *args, **kwargs):
        activity = activity_class(*args, **kwargs)
        self.xmlMapper.update_activity(activity.id, activity)
        self.refresh_activities()

    def remove_activity(self, activity_id):
        self.xmlMapper.remove_activity(activity_id)
        self.refresh_activities()

    def get_nearby_devices(self):
        devices = []
        if self.conf.bluetoothSupport == "Yes":
            self.logger.debug("Searching for Bluetooth devices")
            devices += self.btMgr.get_nearby_devices()
        if self.conf.antSupport == "Yes":
            self.logger.debug("Searching for ANT+ Devices")
            devices += self.antMgr.get_nearby_devices()
        return devices

    def run_test(self, notify_window, name, mac, dev_type):
        device = None
        if dev_type == "BT":
            device = PolariWL(mac)
        elif dev_type == "ANT+":
            device = ANTDevice()
        device.connect()
        self.test_thread = device.run_test(notify_window)
        return device

    def end_bt_test(self, device):
        device.finish_test()
        if self.test_thread.is_alive():
            self.test_thread.join()
        device.disconnect()

    @staticmethod
    def get_supported_devices():
        return ["Polar iWL", "ANT+ HR Band"]

    def is_demo_mode(self):
        return self.conf.defaultMode == "Demo mode"

    def begin_acquisition(self, file_path, activity_id, mode, dev_name, dev_type, dev_dir=None, output="text"):
        if output == "text":
            self.acquisition_path = file_path
            writer = TextWriter(file_path + ".tag.txt", file_path + ".rr.txt")
        if mode == DEMO_MODE:
            device = DemoBand()
            activity = self.xmlMapper.get_activity(activity_id)
            ad = AcquisitionFacade(activity, device, writer)
            ad.start()
        elif mode == DEVICE_CONNECTED_MODE:
            if dev_type == "BT" and dev_name == "Polar iWL":
                device = PolariWL(dev_dir)
                activity = self.xmlMapper.get_activity(activity_id)
                ad = AcquisitionFacade(activity, device, writer)
                ad.start()
            elif dev_type == "ANT+" and dev_name == "ANT+ HR Band":
                device = ANTDevice()
                activity = self.xmlMapper.get_activity(activity_id)
                ad = AcquisitionFacade(activity, device, writer)
                ad.start()

    @run_in_thread
    def open_ghrv(self):
        rr_file = str(self.acquisition_path) + ".rr.txt"
        tag_file = str(self.acquisition_path) + ".tag.txt"
        os.system("/usr/bin/gHRV -loadBeatTXT {0} -loadEpTXT {1}".format(rr_file, tag_file))

    @run_in_thread
    def plot_results(self):
        rr_file = str(self.acquisition_path) + ".rr.txt"
        tag_file = str(self.acquisition_path) + ".tag.txt"
        paint(rr_file, tag_file)





