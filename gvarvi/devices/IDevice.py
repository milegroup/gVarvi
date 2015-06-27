# coding=utf-8
from abc import ABCMeta, abstractmethod


class IDevice:
    """
    Interface that provides common methods for all devices.
    """

    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def find(cls):
        """
        Class method that returns a list of nearby devices.
        """
        pass

    @abstractmethod
    def connect(self, *args):
        """
        Connects to acquisition device.
        @param args: List of parameter values.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnects acquisition device.
        """
        pass

    @abstractmethod
    def run_test(self, notify_window):
        """
        Runs test for device and sends data to a custom window.
        @param notify_window: The target window.
        """
        pass

    @abstractmethod
    def finish_test(self):
        """
        Finishes test for device.
        """
        pass

    @abstractmethod
    def begin_acquisition(self, writer):
        """
        Starts acquisition and writes result data.
        @param writer: Object that writes the result data.
        """
        pass

    @abstractmethod
    def finish_acquisition(self):
        """
        Finishes acquisition
        """
        pass


