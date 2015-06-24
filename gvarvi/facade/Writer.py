# coding=utf-8

from datetime import timedelta
import unicodedata
import sys

__author__ = 'nico'

from abc import ABCMeta, abstractmethod
from logger import Logger
import os
import codecs
from utils import FailedAcquisition


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
        with codecs.open(self.tag_file, "wt", "utf-8") as f:
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

        try:
            reload(sys)
            sys.setdefaultencoding("utf-8")

            def normalize(input_str):
                """
                Removes accents of a string.
                @param input_str: Original string.
                @return: Same string with all accents removed.
                """
                input_str = input_str.lower()
                nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
                return u"".join([c.replace(' ', '_').encode('utf-8') for c in nkfd_form if not unicodedata.combining(
                    c)])

            with codecs.open(self.tag_file, "at", "utf-8") as f:
                line = "{0}\t{1}\t{2:3f}".format(str(timedelta(seconds=beg)),
                                                 normalize(name),
                                                 end - beg)
                f.write(line + os.linesep)

        except Exception as e:
            raise FailedAcquisition("Unable to write tag value in text file{0}Exception type: {0}".format(os.linesep,
                                                                                                          e.__class__.__name__))

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
        with codecs.open(self.rr_file, "wt", "utf-8") as f:
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
