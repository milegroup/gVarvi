# coding=utf-8
__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity, AbstractTag
from player.AssociatedKeyActivityPlayer import AssociatedKeyActivityPlayer


class AssociatedKeyActivity(AbstractActivity):
    name = "Associated-Key tagged activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags

    def run(self, writer):
        self.player = AssociatedKeyActivityPlayer(self.tags)
        self.player.play(writer)


class AssociatedKeyTag(AbstractTag):
    def __init__(self, name, screentext, key):
        AbstractTag.__init__(self, name)
        self.screentext = screentext
        self.key = key

    def check_files(self):
        return True
