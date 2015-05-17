# coding=utf-8
__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity
from player.ManualActivityPlayer import ManualActivityPlayer


class ManualDefinedActivity(AbstractActivity):
    name = "Manual defined activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags

    def run(self, writer):
        ManualActivityPlayer(self.tags).play(writer)

    def __str__(self):
        toret = "Manual defined acivity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n".format(id=self.id,
                                        name=self.name.encode())
        for tag in self.tags:
            toret += "Manual defined tag:\n" \
                     "\tName: {name}\n" \
                     "\tScreen text: {screentext}\n" \
                     "\tFinish type: {finishtype}\n" \
                     "\tTime: {time}\n".format(name=tag.name.encode('utf-8'),
                                               screentext=tag.screentext,
                                               finishtype=tag.finish_type,
                                               time=tag.time)
        return toret


class ManualDefinedTag(object):
    def __init__(self, name, screentext, finish_type, time):
        self.name = name
        self.screentext = screentext
        self.finish_type = finish_type
        self.time = time

    def check_files(self):
        return True