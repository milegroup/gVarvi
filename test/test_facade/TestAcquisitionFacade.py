# coding=utf-8

__author__ = 'nico'

import unittest
import threading

from mockito import *

from facade.AcquisitionFacade import AcquisitionFacade
from devices.IDevice import IDevice
from facade.Writer import IWriter
from activities.AbstractActivity import AbstractActivity
from utils import MissingFiles, HostDownError, AbortedAcquisition


class TestAcquisitionFacade(unittest.TestCase):
    def setUp(self):
        self.mocked_writer = mock(IWriter)
        self.mocked_device = mock(IDevice)
        when(self.mocked_device).begin_acquisition(self.mocked_writer).thenReturn(threading.Thread())
        self.mocked_activity = mock(AbstractActivity)
        when(self.mocked_activity).check_before_run().thenReturn(True)
        self.acquisition_facade = AcquisitionFacade(self.mocked_activity, self.mocked_device, self.mocked_writer)

    def test_start(self):
        self.acquisition_facade.start()
        verify(self.mocked_activity).check_before_run()
        verify(self.mocked_device).connect()
        verify(self.mocked_device).begin_acquisition(self.mocked_writer)
        verify(self.mocked_device).finish_acquisition()

    def test_raise_missing_files_exception(self):
        when(self.mocked_activity).check_before_run().thenReturn(False)
        self.assertRaises(MissingFiles, self.acquisition_facade.start)

    def test_raise_host_down_error(self):
        when(self.mocked_device).connect().thenRaise(HostDownError())
        self.assertRaises(HostDownError, self.acquisition_facade.start)

    def test_raise_aborted_acquisition(self):
        when(self.mocked_activity).run(self.mocked_writer).thenRaise(AbortedAcquisition())
        self.assertRaises(AbortedAcquisition, self.acquisition_facade.start)