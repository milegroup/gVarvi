# coding=utf-8
import shutil
import uuid
import os

from utils import pack_folder_and_remove, unpack_tar_file_and_remove
from activities.AbstractActivity import AbstractActivity
from player.VideoPresentationPlayer import VideoPresentationPlayer





# from player.VideoPresentationPlayerVLC import VideoPresentationPlayer
from config import EXIT_ABORT_CODE, CONF_DIR


class VideoPresentation(AbstractActivity):
    name = "Video presentation"

    def __init__(self, id, name, random, tags):
        AbstractActivity.__init__(self, id, name)
        self.random = random
        self.tags = tags
        self.player = None

    def run(self, writer):
        self.player = VideoPresentationPlayer(self.random, self.tags)
        exit_code = self.player.play(writer)
        if exit_code == EXIT_ABORT_CODE:
            raise KeyboardInterrupt()

    def stop(self):
        self.player.stop()

    def __str__(self):
        toret = "Video presentation activity:\n" \
                "Id: {id}\n" \
                "Name: {name}\n" \
                "Random: {random}\n".format(id=self.id,
                                            name=self.name,
                                            random=self.random)
        for tag in self.tags:
            toret += "Video presentation tag:\n" \
                     "\tName: {name}\n" \
                     "\tPath: {path}\n".format(name=tag.name,
                                               path=tag.path)
        return toret

    def export_to_file(self, file_path):
        from dao.XMLUtils import dump_activity_to_file

        AUX_FOLDER = os.path.join(os.path.expanduser('~'), "activity_auxiliary_folder")
        try:
            os.mkdir(AUX_FOLDER)
        except OSError:
            shutil.rmtree(AUX_FOLDER)
            os.mkdir(AUX_FOLDER)
        with open(os.path.join(AUX_FOLDER, "video.xml"), "wt") as f:
            dump_activity_to_file(self, f)
        for i, t in enumerate(self.tags):
            # Make one aux folder for each tag to place media files
            tag_folder = os.path.join(AUX_FOLDER, str(i))
            os.mkdir(tag_folder)
            file_name = os.path.basename(t.path)
            shutil.copyfile(t.path, os.path.join(tag_folder, file_name))
        pack_folder_and_remove(AUX_FOLDER, file_path)

    @classmethod
    def import_from_file(cls, file_path):
        from dao.XMLUtils import get_activity_object_from_xml

        activity_folder = CONF_DIR
        unpack_tar_file_and_remove(file_path, activity_folder)
        folder_name = os.path.join(activity_folder, str(uuid.uuid4()))
        os.rename(os.path.join(activity_folder, "activity_auxiliary_folder"), folder_name)
        with open(os.path.join(folder_name, "video.xml"), "rt") as f:
            activity = get_activity_object_from_xml(f)
        for i, tag in enumerate(activity.tags):
            tag.path = os.path.join(folder_name, str(i), os.path.basename(tag.path))
        return activity


class VideoTag(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def check_files(self):
        return os.path.isfile(self.path)
