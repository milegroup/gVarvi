# coding=utf-8
__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity, AbstractTag
from player.ManualActivityPlayer import ManualActivityPlayer


class ManualDefinedActivity(AbstractActivity):
    name = "Manual-defined tagged activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags

    def run(self, writer):
        self.player = ManualActivityPlayer(self.tags)
        self.player.play(writer)


class ManualDefinedTag(AbstractTag):
    def __init__(self, name, screentext, finish_type, time):
        AbstractTag.__init__(self, name)
        self.screentext = screentext
        self.finish_type = finish_type
        self.time = time

    def check_files(self):
        return True