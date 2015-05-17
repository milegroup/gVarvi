# coding=utf-8
__author__ = 'nico'

import os

from activities.AbstractActivity import AbstractActivity
from player.VideoPresentationPlayer import VideoPresentationPlayer
from config import EXIT_ABORT_CODE


class VideoPresentation(AbstractActivity):
    name = "Video presentation"

    def __init__(self, id, name, random, tags):
        AbstractActivity.__init__(self, id, name)
        self.random = random
        self.tags = tags

    def run(self, writer):
        exit_code = VideoPresentationPlayer(self.random, self.tags).play(writer)
        if exit_code == EXIT_ABORT_CODE:
            raise KeyboardInterrupt()

    def __str__(self):
        toret = "Video presentation acivity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n" \
                "Random: {random}\n".format(id=self.id,
                                            name=self.name.encode(),
                                            random=self.random)
        for tag in self.tags:
            toret += "Video presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tPath: {path}\n".format(name=tag.name.encode('utf-8'),
                                               path=tag.path)
        return toret


class VideoTag(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def check_files(self):
        return os.path.isfile(self.path)
