# coding=utf-8
__author__ = 'nico'

import os

from activities.AbstractActivity import AbstractActivity
from player.SoundPresentationPlayer import SoundPresentationPlayer


class SoundPresentation(AbstractActivity):
    name = "Sound presentation"

    def __init__(self, id, name, random, tags):
        AbstractActivity.__init__(self, id, name)
        self.random = random
        self.tags = tags

    def run(self, writer):
        SoundPresentationPlayer(self.random, self.tags).play(writer)

    def __str__(self):
        toret = "Sound presentation acivity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n" \
                "Random: {random}\n".format(id=self.id,
                                            name=self.name.encode(),
                                            random=self.random)
        for tag in self.tags:
            toret += "Sound presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tPath: {path}\n" \
                     "\tRandomized images: {random}\n" \
                     "\tAssociated images: {associated_image}\n".format(name=tag.name.encode('utf-8'),
                                                                        path=tag.path,
                                                                        random=tag.random,
                                                                        associated_image=tag.associated_image)
            for image in tag.images:
                toret += "\tImage:\n" \
                         "\t\tPath: {path}\n".format(path=image.path)
        return toret


class SoundPresentationTag(object):
    def __init__(self, name, path, random, associated_image="No", images=None):
        self.name = name
        self.path = path
        self.random = random
        self.associated_image = associated_image
        if not images:
            self.images = []
        else:
            self.images = images

    def check_files(self):
        if not os.path.isfile(self.path):
            return False
        for img in self.images:
            if not os.path.isfile(img.path):
                return False
        return True


class Image(object):
    def __init__(self, path):
        self.path = path

