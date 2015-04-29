# coding=utf-8
__author__ = 'nico'

from abc import ABCMeta, abstractmethod

from config import EXIT_ABORT_CODE, EXIT_SUCCESS_CODE, EXIT_FAIL_CODE
from Utils import AbortedAcquisition, FailedAcquisition


class Player:
    __metaclass__ = ABCMeta

    @abstractmethod
    def play(self, writer):
        pass

    @staticmethod
    def raise_if_needed(code):
        dic = {EXIT_SUCCESS_CODE: None, EXIT_FAIL_CODE: FailedAcquisition, EXIT_ABORT_CODE: AbortedAcquisition}
        if dic[code]:
            raise dic[code]()

