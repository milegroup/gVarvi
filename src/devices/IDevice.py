# coding=utf-8
from abc import ABCMeta, abstractmethod


__author__ = 'nico'


class IDevice:
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def find(cls):
        pass

    @abstractmethod
    def connect(self, *args):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def run_test(self, notify_window):
        pass

    @abstractmethod
    def finish_test(self):
        pass

    @abstractmethod
    def begin_acquisition(self, writer):
        pass

    @abstractmethod
    def finish_acquisition(self):
        pass


