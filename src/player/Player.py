# coding=utf-8
__author__ = 'nico'

from abc import ABCMeta, abstractmethod

from config import EXIT_ABORT_CODE, EXIT_SUCCESS_CODE, EXIT_FAIL_CODE
from Utils import AbortedAdquisiton, FailedAdquisition


class AbstractPlayer:
    __metaclass__ = ABCMeta

    @abstractmethod
    def play(self, writer):
        pass

    def raise_if_needed(self, code):
        dic = {EXIT_SUCCESS_CODE: None, EXIT_FAIL_CODE: FailedAdquisition, EXIT_ABORT_CODE: AbortedAdquisiton}
        if dic[code]:
            raise dic[code]()

