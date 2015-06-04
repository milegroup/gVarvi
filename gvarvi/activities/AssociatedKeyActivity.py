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

    def __str__(self):
        toret = "Associated key activity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n".format(id=self.id,
                                        name=self.name.encode())
        for tag in self.tags:
            toret += "Photo presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tScreen text: {screentext}\n" \
                     "\tAssociated key: {key}\n".format(name=tag.name.encode('utf-8'),
                                                        screentext=tag.screentext,
                                                        key=tag.key)
        return toret


class AssociatedKeyTag(object):
    def __init__(self, name, screentext, key):
        self.name = name
        self.screentext = screentext
        self.key = key

    @staticmethod
    def check_files():
        return True
