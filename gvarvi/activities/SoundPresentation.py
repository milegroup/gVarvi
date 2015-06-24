# coding=utf-8
__author__ = 'nico'
import shutil
import os
import uuid

from utils import pack_folder_and_remove, unpack_tar_file_and_remove
from activities.AbstractActivity import AbstractActivity
from player.SoundPresentationPlayer import SoundPresentationPlayer
from config import CONF_DIR


class SoundPresentation(AbstractActivity):
    name = "Sound presentation"

    def __init__(self, id, name, random, tags):
        AbstractActivity.__init__(self, id, name)
        self.random = random
        self.tags = tags
        self.player = SoundPresentationPlayer(self.random, self.tags)

    def run(self, writer):
        self.player.play(writer)

    def stop(self):
        self.player.stop()

    def __str__(self):
        toret = "Sound presentation acivity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n" \
                "Random: {random}\n".format(id=self.id,
                                            name=self.name.encode('utf-8'),
                                            random=self.random)
        for tag in self.tags:
            toret += "Sound presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tPath: {path}\n" \
                     "\tRandomized images: {random}\n" \
                     "\tAssociated images: {associated_image}\n".format(name=tag.name.encode('utf-8'),
                                                                        path=tag.path.encode('utf-8'),
                                                                        random=tag.random,
                                                                        associated_image=tag.associated_image)
            for image in tag.images:
                toret += "\tImage:\n" \
                         "\t\tPath: {path}\n".format(path=image.path.encode('utf-8'))
        return toret

    def export_to_file(self, file_path):
        from dao.XMLUtils import dump_activity_to_file

        AUX_FOLDER = os.path.join(os.path.expanduser('~'), "activity_auxiliary_folder")
        try:
            os.mkdir(AUX_FOLDER)
        except OSError:
            shutil.rmtree(AUX_FOLDER)
            os.mkdir(AUX_FOLDER)
        with open(os.path.join(AUX_FOLDER, "sound.xml"), "wt") as f:
            dump_activity_to_file(self, f)
        for i, t in enumerate(self.tags):
            # Make one aux folder for each tag to place media files
            tag_folder = os.path.join(AUX_FOLDER, str(i))
            os.mkdir(tag_folder)
            file_name = os.path.basename(t.path)
            shutil.copyfile(t.path, os.path.join(tag_folder, file_name))
            if len(t.images) > 0:
                images_dir = os.path.join(tag_folder, "images")
                try:
                    os.mkdir(images_dir)
                except OSError:
                    shutil.rmtree(images_dir)
                    os.mkdir(images_dir)
                for image in t.images:
                    file_name = os.path.basename(image.path)
                    shutil.copyfile(image.path, os.path.join(images_dir, file_name))
        pack_folder_and_remove(AUX_FOLDER, file_path)

    @classmethod
    def import_from_file(cls, file_path):
        from dao.XMLUtils import get_activity_object_from_xml

        activity_folder = CONF_DIR
        unpack_tar_file_and_remove(file_path, activity_folder)
        folder_name = os.path.join(activity_folder, str(uuid.uuid4()))
        os.rename(os.path.join(activity_folder, "activity_auxiliary_folder"), folder_name)
        with open(os.path.join(folder_name, "sound.xml"), "rt") as f:
            activity = get_activity_object_from_xml(f)
        for i, tag in enumerate(activity.tags):
            tag.path = os.path.join(folder_name, str(i), os.path.basename(tag.path))
            for image in tag.images:
                image.path = os.path.join(os.path.dirname(tag.path), "images", os.path.basename(image.path))
        return activity


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
