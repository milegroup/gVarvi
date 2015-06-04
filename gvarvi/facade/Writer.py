# coding=utf-8

from datetime import timedelta

__author__ = 'nico'

from abc import ABCMeta, abstractmethod
from logger import Logger
import os


class IWriter:
    """
    Interface that provides common methods for every results writer.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def write_tag_value(self, beg, duration, name):
        """
        Writes tag info when tag playing ends.
        @param beg: Begin time in seconds.
        @param duration: Total duration in seconds.
        @param name: Tag name.
        """
        pass

    @abstractmethod
    def write_rr_value(self, value):
        """
        Writes rr value.
        @param value: The value.
        """
        pass

    @abstractmethod
    def close_writer(self):
        """
        Finishes writing operation.
        """
        pass

    @abstractmethod
    def abort(self):
        """
        Aborts writing operation.
        """
        pass


class TextWriter(IWriter):
    """
    IWriter implementation that writes acquisition results to text files.
    @param tag_file: Absolute path to tag file.
    @param rr_file: Absolute path to rr file.
    """

    def __init__(self, tag_file, rr_file):
        self.logger = Logger()

        self.tag_file = tag_file
        with open(self.tag_file, "wt") as f:
            f.write("Init_time\tEvent\tDurat" + os.linesep)
        self.rr_file = rr_file
        self.rr_values = []

    def write_tag_value(self, name, beg, end):
        """
        Writes tag info to tag text file when tag playing ends.
        @param name: Tag name.
        @param beg: Begin time in seconds.
        @param end: End time in seconds.
        """
        with open(self.tag_file, "at") as f:
            line = "%s\t%s\t%.3f" % (str(timedelta(seconds=beg)), name.replace(' ', '_'), end - beg)
            f.write(line + os.linesep)

    def write_rr_value(self, rr):
        """
        Writes rr value to list.
        @param rr: The value.
        """
        self.rr_values.append(rr)

    def close_writer(self):
        """
        Writes list values to text file and closes it.
        """
        with open(self.rr_file, "wt") as f:
            for rr in self.rr_values:
                f.write(str(rr) + os.linesep)

    def abort(self):
        """
        Abort writing operation by removing both text files.
        """
        if os.path.isfile(self.rr_file):
            os.remove(self.rr_file)
        if os.path.isfile(self.tag_file):
            os.remove(self.tag_file)
