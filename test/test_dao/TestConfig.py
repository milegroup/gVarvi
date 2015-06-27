# coding=utf-8

from TestDAO import TestDAO
from config import UserConfig


class TestConfig(TestDAO):
    def setUp(self):
        super(TestConfig, self).setUp()

    def test_read_config(self):
        config = self.mapper.read_config_file()
        self.assertIsInstance(config, UserConfig, "Configuration retrieved from xml must be 'UserConfig' instance")
        self.assertIn("defaultMode", config.__dict__, "Configuration does not have 'defaultMode' parameter")
        self.assertEqual(config.defaultMode, "Demo mode", "Default mode must be demo mode")
        self.assertIn("bluetoothSupport", config.__dict__, "Configuration does not have 'bluetoothSupport' parameter")
        self.assertEqual(config.bluetoothSupport, "No", "Configuration must not have bluetooth support")
        self.assertIn("antSupport", config.__dict__, "Configuration does not have 'antSupport' parameter")
        self.assertEqual(config.antSupport, "No", "Configuration must not have ant support")
        self.assertIn("scanDevicesOnStartup", config.__dict__,
                      "Configuration does not have 'scanDevicesOnStartup' parameter")
        self.assertEqual(config.scanDevicesOnStartup, "Yes", "Configuration must have scanDevicesOnStartup activated")

        self.assertIn("remoteDebugger", config.__dict__, "Configuration does not have 'remoteDebugger' parameter")
        self.assertEqual(config.remoteDebugger, "No", "Configuration must not have remoteDebugger activated")

        self.assertIn("rdIP", config.__dict__, "Configuration does not have 'rdIP' parameter")
        self.assertEqual(config.rdIP, "10.20.30.40", "Remote debugger port IP must be '10.20.30.40'")

        self.assertIn("rdPort", config.__dict__, "Configuration does not have 'rdPort' parameter")
        self.assertEqual(config.rdPort, "4444", "Remote debugger port must be '4444'")

    def test_save_config(self):
        config_dict = {
            "defaultMode": "Device connected mode",
            "bluetoothSupport": "No",
            "antSupport": "Yes",
            "scanDevicesOnStartup": "Yes",
            "remoteDebugger": "Yes",
            "rdIP": "1.1.1.1",
            "rdPort": "1943"
        }
        self.mapper.save_config(config_dict)
        with open(self.mapper.conf_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<config>
    <defaultMode>Device connected mode</defaultMode>
    <bluetoothSupport>No</bluetoothSupport>
    <antSupport>Yes</antSupport>
    <scanDevicesOnStartup>Yes</scanDevicesOnStartup>
    <remoteDebugger>Yes</remoteDebugger>
    <rdIP>1.1.1.1</rdIP>
    <rdPort>1943</rdPort>
</config>""")

    def test_reset_config(self):
        self.mapper.reset_config()
        with open(self.mapper.conf_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<config>
    <defaultMode>Demo mode</defaultMode>
    <bluetoothSupport>Yes</bluetoothSupport>
    <antSupport>Yes</antSupport>
    <scanDevicesOnStartup>No</scanDevicesOnStartup>
    <remoteDebugger>No</remoteDebugger>
    <rdIP>10.10.10.10</rdIP>
    <rdPort>8888</rdPort>
</config>""")


