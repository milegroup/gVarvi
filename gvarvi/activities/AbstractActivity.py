# coding=utf-8
__author__ = 'nico'

from abc import abstractmethod, ABCMeta


class AbstractActivity:
    __metaclass__ = ABCMeta

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tags = None

    def check_before_run(self):
        tags_ok = True
        for tag in self.tags:
            if not tag.check_files():
                tags_ok = False
                break
        return tags_ok

    @abstractmethod
    def run(self, writer):
        pass
