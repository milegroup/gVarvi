# coding=utf-8
__author__ = 'nico'

from Utils import HostDownError, FailedAdquisition, AbortedAdquisiton, MissingFiles
from logger import Logger


class AdquisitionFacade(object):
    """
    Class that directs all the adquisition process,
    including the comunication with adquisition devices
    and activities
    :param activity: The activity to be played
    :param device: The device that performs HRV adquisition
    :param writer: Class that write the results
    """

    def __init__(self, activity, device, writer):
        self.logger = Logger()
        self.activity = activity
        self.device = device
        self.writer = writer

        self.adquisition_thread = None
        self.event_thread = None

    def start(self):
        try:
            if self.activity.check_before_run():
                self.logger.info("Connecting to device")
                self.device.connect()
                self.logger.info("Starting adquisition")
                import time
                self.adquisition_thread = self.device.begin_adquisition(self.writer)
                print "After begin adquisition: {0}".format(time.time())
                # Run device adquisition before activity because
                # adquisition will be executed in a new thread so
                # doesn't block program
                self.logger.info("Running activity")
                print "Before run activity: {0}".format(time.time())
                self.activity.run(self.writer)
                self.logger.info("Activity ended. Finishing device adquisition")
                self.device.finish_adquisition()
                print "After finish adquisition: {0}".format(time.time())
                self.adquisition_thread.join()
                self.logger.info("Disconnecting device")
                self.device.disconnect()
                print "After disconnect device: {0}".format(time.time())
                self.logger.info("Device disconnected. Adquisition finished")
            else:
                self.logger.exception("Some of activity files has been deleted")
                raise MissingFiles()

        except HostDownError:
            self.logger.exception("Unable to connect to device (host down)")
            raise
        except FailedAdquisition:
            self.logger.exception("Adquisition failed. Data will be saved anyway")
            raise
        except AbortedAdquisiton:
            self._abort()
            self.logger.info("Activity aborted. Data won't be saved")
            raise

    def _abort(self):
        self.device.finish_adquisition()
        if self.adquisition_thread:
            self.adquisition_thread.join()
        self.device.disconnect()
        self.writer.abort()
