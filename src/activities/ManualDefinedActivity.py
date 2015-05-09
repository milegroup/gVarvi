# coding=utf-8
__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity
from player.ManualActivityPlayer import ManualActivityPlayer


class ManualDefinedActivity(AbstractActivity):
    name = "Manual-defined tagged activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags

    def run(self, writer):
        ManualActivityPlayer(self.tags).play(writer)


class ManualDefinedTag(object):
    def __init__(self, name, screentext, finish_type, time):
        self.name = name
        self.screentext = screentext
        self.finish_type = finish_type
        self.time = time

    def check_files(self):
        return True