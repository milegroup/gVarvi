# coding=utf-8
__author__ = 'nico'

from abc import abstractmethod, ABCMeta


class AbstractActivity:
    """
    Abstract class that provides common methods and attributes
    to every activities.
    @param id: Unique identifier for each activity.
    @param name: Name of the activity.
    """
    __metaclass__ = ABCMeta

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tags = None

    def check_before_run(self):
        """
        Checks if every activity tag is ok and there is no missing
        files.
        @return: True if everything is OK.
        """
        tags_ok = True
        for tag in self.tags:
            if not tag.check_files():
                tags_ok = False
                break
        return tags_ok

    @abstractmethod
    def run(self, writer):
        """
        Plays the activity.
        @param writer: Object that writes tag data.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stops the activity
        """
        pass

    @classmethod
    @abstractmethod
    def import_from_file(cls, file_path):
        pass

    @abstractmethod
    def export_to_file(self, file_path):
        pass
