# coding=utf-8
__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity
from player.AssociatedKeyActivityPlayer import AssociatedKeyActivityPlayer


class AssociatedKeyActivity(AbstractActivity):
    name = "Associated-Key tagged activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags

    def run(self, writer):
        AssociatedKeyActivityPlayer(self.tags).play(writer)


class AssociatedKeyTag(object):
    def __init__(self, name, screentext, key):
        self.name = name
        self.screentext = screentext
        self.key = key

    @staticmethod
    def check_files():
        return True
