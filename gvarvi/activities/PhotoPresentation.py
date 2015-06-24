# coding=utf-8

__author__ = 'nico'

import uuid
import os
import shutil

from activities.AbstractActivity import AbstractActivity
from player.PhotoPresentationPlayer import PhotoPresentationPlayer
from config import SUPPORTED_IMG_EXTENSIONS, CONF_DIR
from utils import get_folder_images, pack_folder_and_remove, unpack_tar_file_and_remove


class PhotoPresentation(AbstractActivity):
    name = "Photo presentation"

    def __init__(self, id, name, random, gap, tags):
        AbstractActivity.__init__(self, id, name)
        self.random = random
        self.gap = gap
        self.tags = tags
        self.player = PhotoPresentationPlayer(self.gap, self.random, self.tags)

    def run(self, writer):
        self.player.play(writer)

    def stop(self):
        self.player.stop()

    def __str__(self):
        toret = "Photo presentation acivity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n" \
                "Random: {random}\n" \
                "Gap: {gap}\n".format(id=self.id,
                                      name=self.name.encode('utf-8'),
                                      random=self.random,
                                      gap=self.gap)
        for tag in self.tags:
            toret += "Photo presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tPath: {path}\n" \
                     "\tAssociated sound: {associated_sound}\n".format(name=tag.name.encode('utf-8'),
                                                                       path=tag.path.encode('utf-8'),
                                                                       associated_sound=tag.associated_sound)
            for sound in tag.sounds:
                toret += "\tSound:\n" \
                         "\t\tPath: {path}\n".format(path=sound.path.encode('utf-8'))
        return toret

    def export_to_file(self, file_path):
        from dao.XMLUtils import dump_activity_to_file

        AUX_FOLDER = os.path.join(os.path.expanduser('~'), "activity_auxiliary_folder")
        try:
            os.mkdir(AUX_FOLDER)
        except OSError:
            shutil.rmtree(AUX_FOLDER)
            os.mkdir(AUX_FOLDER)
        with open(os.path.join(AUX_FOLDER, "photo.xml"), "wt") as f:
            dump_activity_to_file(self, f)
        for i, t in enumerate(self.tags):
            # Make one aux folder for each tag to place media files
            tag_folder = os.path.join(AUX_FOLDER, str(i))
            os.mkdir(tag_folder)
            for img in get_folder_images(t.path):
                file_name = os.path.basename(img)
                shutil.copyfile(img, os.path.join(tag_folder, file_name))
                if len(t.sounds) > 0:
                    sounds_dir = os.path.join(tag_folder, "sounds")
                    try:
                        os.mkdir(sounds_dir)
                    except OSError:
                        shutil.rmtree(sounds_dir)
                        os.mkdir(sounds_dir)
                    for sound in t.sounds:
                        file_name = os.path.basename(sound.path)
                        shutil.copyfile(sound.path, os.path.join(sounds_dir, file_name))
        pack_folder_and_remove(AUX_FOLDER, file_path)

    @classmethod
    def import_from_file(cls, file_path):
        from dao.XMLUtils import get_activity_object_from_xml

        activity_folder = CONF_DIR
        unpack_tar_file_and_remove(file_path, activity_folder)
        folder_name = os.path.join(activity_folder, str(uuid.uuid4()))
        os.rename(os.path.join(activity_folder, "activity_auxiliary_folder"), folder_name)
        with open(os.path.join(folder_name, "photo.xml"), "rt") as f:
            activity = get_activity_object_from_xml(f)
        for i, tag in enumerate(activity.tags):
            tag.path = os.path.join(folder_name, str(i))
            for sound in tag.sounds:
                sound.path = os.path.join(tag.path, "sounds", os.path.basename(sound.path))
        return activity


class PhotoPresentationTag(object):
    def __init__(self, name, path, associated_sound, sounds=None):
        self.name = name
        self.path = path
        self.associated_sound = associated_sound
        if not sounds:
            self.sounds = []
        else:
            self.sounds = sounds

    def check_files(self):
        images = [os.path.join(self.path, img) for img in os.listdir(self.path) if
                  img.endswith(SUPPORTED_IMG_EXTENSIONS)]
        if len(images) == 0:
            return False
        for sound in self.sounds:
            if not os.path.isfile(sound.path):
                return False
        return True


class Sound(object):
    def __init__(self, path):
        self.path = path
