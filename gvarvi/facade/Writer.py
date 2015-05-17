# coding=utf-8

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
    def __init__(self, tag_file, rr_file):
        self.logger = Logger()

        self.tag_file = tag_file
        with open(self.tag_file, "w") as f:
            f.write("Init_time\tEvent\tDurat\n")
        self.rr_file = rr_file
        self.rr_values = []

    def write_tag_value(self, name, beg, end):
        with open(self.tag_file, "a") as f:
            line = "%s\t%s\t%.3f" % (str(timedelta(seconds=beg)), name.replace(' ', '_'), end - beg)
            f.write(line + "\n")

    def write_rr_value(self, rr):
        self.rr_values.append(rr)

    def close_writer(self):
        self.logger.debug("Writing all rr values")
        with open(self.rr_file, "w") as f:
            for rr in self.rr_values:
                f.write(str(rr) + "\n")

    def abort(self):
        if os.path.isfile(self.rr_file):
            os.remove(self.rr_file)
        if os.path.isfile(self.tag_file):
            os.remove(self.tag_file)




