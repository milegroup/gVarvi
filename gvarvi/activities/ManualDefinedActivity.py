# coding=utf-8
import os
import shutil

from config import CONF_DIR
from utils import pack_folder_and_remove, unpack_tar_file_and_remove

__author__ = 'nico'

from activities.AbstractActivity import AbstractActivity
from player.ManualActivityPlayer import ManualActivityPlayer


class ManualDefinedActivity(AbstractActivity):
    name = "Manual defined activity"

    def __init__(self, id, name, tags):
        AbstractActivity.__init__(self, id, name)
        self.tags = tags
        self.player = ManualActivityPlayer(self.tags)

    def run(self, writer):
        self.player.play(writer)

    def stop(self):
        self.player.stop()

    def __str__(self):
        toret = "Manual defined acivity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n".format(id=self.id,
                                        name=self.name.encode('utf-8'))
        for tag in self.tags:
            toret += "Manual defined tag:\n" \
                     "\tName: {name}\n" \
                     "\tScreen text: {screentext}\n" \
                     "\tFinish type: {finishtype}\n" \
                     "\tTime: {time}\n".format(name=tag.name.encode('utf-8'),
                                               screentext=tag.screentext.encode('utf-8'),
                                               finishtype=tag.finish_type,
                                               time=tag.time)
        return toret

    def export_to_file(self, file_path):
        from dao.XMLUtils import dump_activity_to_file

        AUX_FOLDER = os.path.join(os.path.expanduser('~'), "activity_auxiliary_folder")
        try:
            os.mkdir(AUX_FOLDER)
        except OSError:
            shutil.rmtree(AUX_FOLDER)
            os.mkdir(AUX_FOLDER)
        with open(os.path.join(AUX_FOLDER, "manual.xml"), "wt") as f:
            dump_activity_to_file(self, f)
        pack_folder_and_remove(AUX_FOLDER, file_path)

    @classmethod
    def import_from_file(cls, file_path):
        from dao.XMLUtils import get_activity_object_from_xml

        activity_folder = CONF_DIR
        unpack_tar_file_and_remove(file_path, activity_folder)
        with open(os.path.join(activity_folder, "activity_auxiliary_folder", "manual.xml"), "rt") as f:
            activity = get_activity_object_from_xml(f)
            shutil.rmtree(os.path.join(activity_folder, "activity_auxiliary_folder"))
        return activity


class ManualDefinedTag(object):
    def __init__(self, name, screentext, finish_type, time):
        self.name = name
        self.screentext = screentext
        self.finish_type = finish_type
        self.time = time

    def check_files(self):
        return True
