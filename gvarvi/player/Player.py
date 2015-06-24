# coding=utf-8
__author__ = 'nico'

from abc import ABCMeta, abstractmethod

from config import EXIT_ABORT_CODE, EXIT_SUCCESS_CODE, EXIT_FAIL_CODE
from utils import AbortedAcquisition, FailedAcquisition


class Player:
    __metaclass__ = ABCMeta

    @abstractmethod
    def play(self, writer):
        pass

    @abstractmethod
    def stop(self):
        pass

    @staticmethod
    def raise_if_needed(code):
        """
        Raises an exception based on activity player exit code.
        @param code: Exit code of activity player.
        @raise dic[code]: Exception that method raises if is required by exit code.
        """
        dic = {EXIT_SUCCESS_CODE: None, EXIT_FAIL_CODE: FailedAcquisition, EXIT_ABORT_CODE: AbortedAcquisition}
        if dic.get(code):
            raise dic[code]()

