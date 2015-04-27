from datetime import timedelta

__author__ = 'nico'

from abc import ABCMeta, abstractmethod
from logger import Logger
import os


class IWriter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def write_tag_value(self, beg, duration, name):
        pass

    @abstractmethod
    def write_rr_value(self, value):
        pass

    @abstractmethod
    def close_writer(self):
        pass

    @abstractmethod
    def abort(self):
        pass


class TextWriter(IWriter):
    def __init__(self, tagfile, rrfile):
        self.logger = Logger()

        self.tagFile = tagfile
        with open(self.tagFile, "w") as f:
            f.write("Init_time\tEvent\tDurat\n")
        self.RRFile = rrfile
        self.rr_values = []

    def write_tag_value(self, name, beg, end):
        with open(self.tagFile, "a") as f:
            line = "%s\t%s\t%.3f" % (str(timedelta(seconds=beg)), name.replace(' ', '_'), end - beg)
            #self.logger.debug("Writing tag item:\n\t{0}".format(line))
            f.write(line + "\n")

    def write_rr_value(self, rr):
        #self.logger.debug("RR value:\n\t{0}".format(rr))
        print "Writing {0} bpm".format(rr)
        self.rr_values.append(rr)

    def close_writer(self):
        with open(self.RRFile, "w") as f:
            for rr in self.rr_values:
                f.write(str(rr) + "\n")

    def abort(self):
        if os.path.isfile(self.RRFile):
            os.remove(self.RRFile)
        if os.path.isfile(self.tagFile):
            os.remove(self.tagFile)




