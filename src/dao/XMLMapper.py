# coding=utf-8
__author__ = 'nico'

from shutil import copyfile
import xml.etree.ElementTree as eT

from activities.PhotoPresentation import PhotoPresentation, PhotoPresentationTag, Sound
from activities.VideoPresentation import VideoPresentation, VideoTag
from activities.SoundPresentation import SoundPresentation, SoundPresentationTag, Image
from activities.ManualDefinedActivity import ManualDefinedActivity, ManualDefinedTag
from activities.AssociatedKeyActivity import AssociatedKeyActivity, AssociatedKeyTag
from config import DEFAULT_CONF_FILE, UserConfig


class XMLMapper(object):
    """
    Class that performs CRUD operations over the activities
    in xml and manipulates the xml config file
    :param actfile: Absolute path to xml activities file
    :param conffile: Absolute path to xml config file
    """

    def __init__(self, actfile, conffile):
        self.lastId = 0
        self.act_file = actfile
        self.conf_file = conffile
        self.used_ids = []

    def read_activities_file(self):
        """
        Parses xml activities file to get stored activities
        :return: A list with all stored activity objects
        """
        tree = eT.ElementTree(file=self.act_file)
        root = tree.getroot()
        activities = []
        self.used_ids = []
        for element in root:
            activity = None
            if element.attrib["type"] == PhotoPresentation.name:
                tags = []
                for tagelement in element.findall("tag"):
                    if tagelement.attrib["soundAssociated"] == "Yes":
                        sounds = []
                        for soundElement in tagelement.findall("sound"):
                            sound = Sound(soundElement.attrib["path"])
                            sounds.append(sound)
                        tag = PhotoPresentationTag(
                            tagelement.attrib["name"],
                            tagelement.attrib["path"],
                            tagelement.attrib["soundAssociated"],
                            sounds
                        )
                    else:
                        tag = PhotoPresentationTag(
                            tagelement.attrib["name"],
                            tagelement.attrib["path"],
                            tagelement.attrib["soundAssociated"],
                        )

                    tags.append(tag)
                activity = PhotoPresentation(
                    element.attrib["id"],
                    element.attrib["name"],
                    element.attrib["random"],
                    element.attrib["gap"],
                    tags)

            elif element.attrib["type"] == VideoPresentation.name:
                tags = []
                for tagelement in element.findall("tag"):
                    tag = VideoTag(
                        tagelement.attrib["name"],
                        tagelement.attrib["path"])
                    tags.append(tag)
                activity = VideoPresentation(
                    element.attrib["id"],
                    element.attrib["name"],
                    element.attrib["random"],
                    tags
                )

            elif element.attrib["type"] == SoundPresentation.name:
                tags = []
                for tagelement in element.findall("tag"):
                    images = []
                    for image_element in tagelement.findall("image"):
                        image = Image(image_element.attrib["path"])
                        images.append(image)
                    tag = SoundPresentationTag(
                        tagelement.attrib["name"],
                        tagelement.attrib["path"],
                        tagelement.attrib["random"],
                        tagelement.attrib["imageAssociated"],
                        images)
                    tags.append(tag)
                activity = SoundPresentation(
                    element.attrib["id"],
                    element.attrib["name"],
                    element.attrib["random"],
                    tags
                )

            elif element.attrib["type"] == ManualDefinedActivity.name:
                tags = []
                for tag_element in element.findall("tag"):
                    tag = ManualDefinedTag(
                        tag_element.attrib["name"],
                        tag_element.attrib["text"],
                        tag_element.attrib["finishType"],
                        int(tag_element.attrib["time"])
                    )
                    tags.append(tag)
                activity = ManualDefinedActivity(
                    element.attrib["id"],
                    element.attrib["name"],
                    tags
                )

            elif element.attrib["type"] == AssociatedKeyActivity.name:
                tags = []
                for tag_element in element.findall("tag"):
                    tag = AssociatedKeyTag(
                        tag_element.attrib["name"],
                        tag_element.attrib["text"],
                        tag_element.attrib["key"]
                    )
                    tags.append(tag)
                activity = AssociatedKeyActivity(
                    element.attrib["id"],
                    element.attrib["name"],
                    tags
                )
            self.used_ids.append(int(element.attrib["id"]))
            activities.append(activity)
        return sorted(activities, key=lambda x: x.id)

    def get_activity(self, activity_id):
        """
        Gets the activity wich id is passed by parameter
        :param activity_id: The id of the activity you want get
        :return: The activity object :raise KeyError: If there is no activity with that id
        """
        tree = eT.ElementTree(file=self.act_file)
        root = tree.getroot()
        for element in root:
            activity = None
            if element.attrib["id"] == str(activity_id):
                if element.attrib["type"] == PhotoPresentation.name:
                    tags = []
                    for tagelement in element.findall("tag"):
                        sounds = []
                        if tagelement.attrib["soundAssociated"] == "Yes":
                            for soundElement in tagelement.findall("sound"):
                                sound = Sound(soundElement.attrib["path"])
                                sounds.append(sound)
                        tag = PhotoPresentationTag(
                            tagelement.attrib["name"],
                            tagelement.attrib["path"],
                            tagelement.attrib["soundAssociated"],
                            sounds
                        )

                        tags.append(tag)
                    activity = PhotoPresentation(
                        element.attrib["id"],
                        element.attrib["name"],
                        element.attrib["random"],
                        int(element.attrib["gap"]),
                        tags)

                elif element.attrib["type"] == VideoPresentation.name:
                    tags = []
                    for tagelement in element.findall("tag"):
                        tag = VideoTag(
                            tagelement.attrib["name"],
                            tagelement.attrib["path"])
                        tags.append(tag)
                    activity = VideoPresentation(
                        element.attrib["id"],
                        element.attrib["name"],
                        element.attrib["random"],
                        tags
                    )

                elif element.attrib["type"] == SoundPresentation.name:
                    tags = []
                    for tagelement in element.findall("tag"):
                        images = []
                        if tagelement.attrib["imageAssociated"] == "Yes":
                            for image_element in tagelement.findall("image"):
                                image = Image(image_element.attrib["path"])
                                images.append(image)
                        tag = SoundPresentationTag(
                            tagelement.attrib["name"],
                            tagelement.attrib["path"],
                            tagelement.attrib["random"],
                            tagelement.attrib["imageAssociated"],
                            images
                        )
                        tags.append(tag)
                    activity = SoundPresentation(
                        element.attrib["id"],
                        element.attrib["name"],
                        element.attrib["random"],
                        tags
                    )

                elif element.attrib["type"] == ManualDefinedActivity.name:
                    tags = []
                    for tag_element in element.findall("tag"):
                        tag = ManualDefinedTag(
                            tag_element.attrib["name"],
                            tag_element.attrib["text"],
                            tag_element.attrib["finishType"],
                            int(tag_element.attrib["time"])
                        )
                        tags.append(tag)
                    activity = ManualDefinedActivity(
                        element.attrib["id"],
                        element.attrib["name"],
                        tags
                    )

                elif element.attrib["type"] == AssociatedKeyActivity.name:
                    tags = []
                    for tag_element in element.findall("tag"):
                        tag = AssociatedKeyTag(
                            tag_element.attrib["name"],
                            tag_element.attrib["text"],
                            tag_element.attrib["key"]
                        )
                        tags.append(tag)
                    activity = AssociatedKeyActivity(
                        element.attrib["id"],
                        element.attrib["name"],
                        tags
                    )
                return activity
        raise KeyError("There isn't any activity with that id: %s" % (str(activity_id)))

    def save_activity(self, activity, updating=False):
        """
        Save the activity passed by parameter to xml
        :param updating: Indicate if saving is performed inside an update process
        :param activity: The activity object
        """
        tree = eT.ElementTree(file=self.act_file)
        root = tree.getroot()

        act_element = eT.Element("activity")
        if updating:
            act_element.attrib["id"] = str(activity.id)
        else:
            act_element.attrib["id"] = str(self._get_next_id())

        act_element.attrib["name"] = activity.name
        act_type = activity.__class__.name

        if act_type == PhotoPresentation.name:
            act_element.attrib["type"] = PhotoPresentation.name
            act_element.attrib["gap"] = str(activity.gap)
            act_element.attrib["random"] = activity.random
            for tag in activity.tags:
                tag_element = eT.Element("tag")
                tag_element.attrib["name"] = tag.name
                tag_element.attrib["path"] = tag.path
                tag_element.attrib["soundAssociated"] = tag.sound_associated
                for sound in tag.sounds:
                    sound_element = eT.Element("sound")
                    sound_element.attrib["path"] = sound.path
                    tag_element.append(sound_element)
                act_element.append(tag_element)

        elif act_type == SoundPresentation.name:
            act_element.attrib["type"] = SoundPresentation.name
            act_element.attrib["random"] = activity.random
            for tag in activity.tags:
                tag_element = eT.Element("tag")
                tag_element.attrib["name"] = tag.name
                tag_element.attrib["path"] = tag.path
                tag_element.attrib["random"] = tag.random
                tag_element.attrib["imageAssociated"] = tag.image_associated
                for image in tag.images:
                    image_element = eT.Element("image")
                    image_element.attrib["path"] = image.path
                    tag_element.append(image_element)
                act_element.append(tag_element)

        elif act_type == VideoPresentation.name:
            act_element.attrib["type"] = VideoPresentation.name
            act_element.attrib["random"] = activity.random
            for tag in activity.tags:
                tag_element = eT.Element("tag")
                tag_element.attrib["name"] = tag.name
                tag_element.attrib["path"] = tag.path
                act_element.append(tag_element)

        elif act_type == ManualDefinedActivity.name:
            act_element.attrib["type"] = ManualDefinedActivity.name
            for tag in activity.tags:
                tag_element = eT.Element("tag")
                tag_element.attrib["name"] = tag.name
                tag_element.attrib["text"] = tag.screentext
                tag_element.attrib["finishType"] = tag.finish_type
                tag_element.attrib["time"] = str(tag.time)
                act_element.append(tag_element)

        elif act_type == AssociatedKeyActivity.name:
            act_element.attrib["type"] = AssociatedKeyActivity.name
            for tag in activity.tags:
                tag_element = eT.Element("tag")
                tag_element.attrib["name"] = tag.name
                tag_element.attrib["text"] = tag.screentext
                tag_element.attrib["key"] = tag.key
                act_element.append(tag_element)

        root.append(act_element)
        eT.ElementTree(root).write(self.act_file, encoding="UTF-8")

    def remove_activity(self, activity_id):
        """
        Removes an activity wich id is passed as a parameter
        :param activity_id: The id of the activity
        """
        tree = eT.ElementTree(file=self.act_file)
        root = tree.getroot()
        for act_element in root:
            if act_element.attrib["id"] == str(activity_id):
                root.remove(act_element)
                break
        eT.ElementTree(root).write(self.act_file, encoding="UTF-8")

    def update_activity(self, activity_id, activity):
        """
        Modifies the activity wich id is passed as a parameter
        with the data of the object activity passed as a parameter.
        Also change activity id to the minimum possible
        :param activity_id: The id of that activity
        :param activity: The activity object with the new data
        """
        self.remove_activity(activity_id)
        self.save_activity(activity, updating=True)

    def read_config_file(self):
        """
        Parses the xml config file and return the configuration
        :return: A Config object with the configuration data
        """
        tree = eT.ElementTree(file=self.conf_file)
        root = tree.getroot()
        conf_dict = {}
        for element in root:
            conf_dict[element.tag] = element.text
        conf = UserConfig(conf_dict)
        return conf

    def reset_config(self):
        """
        Resets the configuration by overriding the
        actual conf file with the default conf file
        """
        copyfile(DEFAULT_CONF_FILE, self.conf_file)

    def save_config(self, attr_dict):
        """
        Saves the actual configuration to xml config file
        :param attr_dict: A dictonary with param configurations and their values
        """
        tree = eT.parse(self.conf_file)
        doc = tree.getroot()
        for key in attr_dict.keys():
            elem = doc.find(key)
            elem.text = str(attr_dict[key])
        eT.ElementTree(doc).write(self.conf_file, encoding="UTF-8")

    def _get_next_id(self):
        if len(self.used_ids) > 0:
            for i in range(1, max(self.used_ids) + 2):
                if i not in self.used_ids:
                    return i
        else:
            return 1
