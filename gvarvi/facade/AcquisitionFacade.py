# coding=utf-8
__author__ = 'nico'

from utils import HostDownError, FailedAcquisition, AbortedAcquisition, MissingFiles
from logger import Logger


class AcquisitionFacade(object):
    """
    Class that directs all the acquisition process,
    including the communication with acquisition devices
    and activities
    @param activity: The activity to be played
    @param device: The device that performs HRV acquisition
    @param writer: Class that write the results
    """

    def __init__(self, activity, device, writer):
        self.logger = Logger()
        self.activity = activity
        self.device = device
        self.writer = writer

        self.acquisition_thread = None
        self.event_thread = None

    def start(self):
        """
        Starts acquisition.
        @raise MissingFiles: If there are missing activity files.
        """
        try:
            if self.activity.check_before_run():
                self.logger.info("Connecting to device")
                self.device.connect()
                self.logger.info("Starting acquisition")

                self.acquisition_thread = self.device.begin_acquisition(self.writer)
                # Run device acquisition before activity because
                # acquisition will be executed in a new thread so
                # doesn't block program
                self.logger.info("Running activity")
                self.activity.run(self.writer)
                self.logger.info("Activity ended. Finishing device acquisition")
                self.device.finish_acquisition()
                if self.acquisition_thread and self.acquisition_thread.is_alive():
                    self.acquisition_thread.join()
                self.logger.info("Disconnecting device")
                self.device.disconnect()
                self.logger.info("Device disconnected. Acquisition finished")
            else:
                self.logger.exception("Some of activity files has been deleted")
                self.writer.abort()
                raise MissingFiles()

        except HostDownError:
            if self.acquisition_thread and self.acquisition_thread.is_alive():
                self.acquisition_thread.join()
            self.logger.exception("Unable to connect to device (host down)")
            raise
        except FailedAcquisition:
            self._abort(remove_files=False)
            if self.acquisition_thread and self.acquisition_thread.is_alive():
                self.acquisition_thread.join()
            self.logger.exception("Acquisition failed. Data will be saved anyway")
            raise
        except AbortedAcquisition:
            self._abort()
            self.logger.info("Activity aborted. Data won't be saved")
            raise
        except Exception as e:
            self._abort(remove_files=False)
            raise FailedAcquisition(e.message)

    def _abort(self, remove_files=True):
        self.activity.stop()
        self.device.finish_acquisition()
        if self.acquisition_thread and self.acquisition_thread.is_alive():
            self.acquisition_thread.join()
        self.device.disconnect()
        if remove_files:
            self.writer.abort()
