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


class VideoTag(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def check_files(self):
        return os.path.isfile(self.path)
