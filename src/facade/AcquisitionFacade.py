# coding=utf-8
__author__ = 'nico'

from Utils import HostDownError, FailedAcquisition, AbortedAcquisition, MissingFiles
from logger import Logger


class AcquisitionFacade(object):
    """
    Class that directs all the acquisition process,
    including the communication with acquisition devices
    and activities
    :param activity: The activity to be played
    :param device: The device that performs HRV acquisition
    :param writer: Class that write the results
    """

    def __init__(self, activity, device, writer):
        self.logger = Logger()
        self.activity = activity
        self.device = device
        self.writer = writer

        self.acquisition_thread = None
        self.event_thread = None

    def start(self):
        try:
            if self.activity.check_before_run():
                self.logger.info("Connecting to device")
                self.device.connect()
                self.logger.info("Starting acquisition")
                import time

                self.acquisition_thread = self.device.begin_acquisition(self.writer)
                # Run device acquisition before activity because
                # acquisition will be executed in a new thread so
                # doesn't block program
                self.logger.info("Running activity")
                self.activity.run(self.writer)
                self.logger.info("Activity ended. Finishing device acquisition")
                self.device.finish_acquisition()
                self.acquisition_thread.join()
                self.logger.info("Disconnecting device")
                self.device.disconnect()
                self.logger.info("Device disconnected. Acquisition finished")
            else:
                self.logger.exception("Some of activity files has been deleted")
                raise MissingFiles()

        except HostDownError:
            self.logger.exception("Unable to connect to device (host down)")
            raise
        except FailedAcquisition:
            self.logger.exception("Acquisition failed. Data will be saved anyway")
            raise
        except AbortedAcquisition:
            self._abort()
            self.logger.info("Activity aborted. Data won't be saved")
            raise

    def _abort(self):
        self.device.finish_acquisition()
        if self.acquisition_thread:
            self.acquisition_thread.join()
        self.device.disconnect()
        self.writer.abort()
