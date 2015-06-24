# coding=utf-8
import os
import shutil

from config import CONF_DIR
from utils import pack_folder_and_remove, unpack_tar_file_and_remove

__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity
from player.AssociatedKeyActivityPlayer import AssociatedKeyActivityPlayer


class AssociatedKeyActivity(AbstractActivity):
    name = "Associated-Key tagged activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags
        self.player = AssociatedKeyActivityPlayer(self.tags)

    def run(self, writer):
        self.player.play(writer)

    def stop(self):
        self.player.stop()

    def __str__(self):
        toret = "Associated key activity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n".format(id=self.id,
                                        name=self.name.encode('utf-8'))
        for tag in self.tags:
            toret += "Photo presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tScreen text: {screentext}\n" \
                     "\tAssociated key: {key}\n".format(name=tag.name.encode('utf-8'),
                                                        screentext=tag.screentext.encode('utf-8'),
                                                        key=tag.key)
        return toret

    def export_to_file(self, file_path):
        from dao.XMLUtils import dump_activity_to_file

        AUX_FOLDER = os.path.join(os.path.expanduser('~'), "activity_auxiliary_folder")
        try:
            os.mkdir(AUX_FOLDER)
        except OSError:
            shutil.rmtree(AUX_FOLDER)
            os.mkdir(AUX_FOLDER)
        with open(os.path.join(AUX_FOLDER, "key.xml"), "wt") as f:
            dump_activity_to_file(self, f)
        pack_folder_and_remove(AUX_FOLDER, file_path)

    @classmethod
    def import_from_file(cls, file_path):
        from dao.XMLUtils import get_activity_object_from_xml

        activity_folder = CONF_DIR
        unpack_tar_file_and_remove(file_path, activity_folder)
        with open(os.path.join(activity_folder, "activity_auxiliary_folder", "key.xml"), "rt") as f:
            activity = get_activity_object_from_xml(f)
            shutil.rmtree(os.path.join(activity_folder, "activity_auxiliary_folder"))
        return activity


class AssociatedKeyTag(object):
    def __init__(self, name, screentext, key):
        self.name = name
        self.screentext = screentext
        self.key = key

    @staticmethod
    def check_files():
        return True
