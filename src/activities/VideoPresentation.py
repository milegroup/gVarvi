# coding=utf-8
__author__ = 'nico'

import os

from activities.AbstractActivity import AbstractActivity, AbstractTag
from player.VideoPresentationPlayer import VideoPresentationPlayer
from config import EXIT_ABORT_CODE


class VideoPresentation(AbstractActivity):
    name = "Video presentation"

    def __init__(self, id, name, random, tags):
        AbstractActivity.__init__(self, id, name)
        self.random = random
        self.tags = tags

    def run(self, writer):
        self.player = VideoPresentationPlayer(self.random, self.tags)
        exit_code = self.player.play(writer)
        if exit_code == EXIT_ABORT_CODE:
            raise KeyboardInterrupt()


class VideoTag(AbstractTag):
    def __init__(self, name, path):
        AbstractTag.__init__(self, name)
        self.path = path

    def check_files(self):
        return os.path.isfile(self.path)
