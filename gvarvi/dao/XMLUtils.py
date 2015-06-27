# coding=utf-8

import xml.etree.ElementTree as eT

import activities.PhotoPresentation
import activities.VideoPresentation
import activities.SoundPresentation
import activities.AssociatedKeyActivity
import activities.ManualDefinedActivity


def dump_activity_to_file(activity, file_path):
    act_element = eT.Element("activity")
    act_element.attrib["id"] = str(activity.id)

    act_element.attrib["name"] = activity.name
    act_type = activity.__class__.name

    if act_type == activities.PhotoPresentation.PhotoPresentation.name:
        act_element.attrib["type"] = activities.PhotoPresentation.PhotoPresentation.name
        act_element.attrib["gap"] = str(activity.gap)
        act_element.attrib["random"] = activity.random
        for tag in activity.tags:
            tag_element = eT.Element("tag")
            tag_element.attrib["name"] = tag.name
            tag_element.attrib["path"] = tag.path
            tag_element.attrib["associatedSound"] = tag.associated_sound
            for sound in tag.sounds:
                sound_element = eT.Element("sound")
                sound_element.attrib["path"] = sound.path
                tag_element.append(sound_element)
            act_element.append(tag_element)

    elif act_type == activities.SoundPresentation.SoundPresentation.name:
        act_element.attrib["type"] = activities.SoundPresentation.SoundPresentation.name
        act_element.attrib["random"] = activity.random
        for tag in activity.tags:
            tag_element = eT.Element("tag")
            tag_element.attrib["name"] = tag.name
            tag_element.attrib["path"] = tag.path
            tag_element.attrib["random"] = tag.random
            tag_element.attrib["associatedImage"] = tag.associated_image
            for image in tag.images:
                image_element = eT.Element("image")
                image_element.attrib["path"] = image.path
                tag_element.append(image_element)
            act_element.append(tag_element)

    elif act_type == activities.VideoPresentation.VideoPresentation.name:
        act_element.attrib["type"] = activities.VideoPresentation.VideoPresentation.name
        act_element.attrib["random"] = activity.random
        for tag in activity.tags:
            tag_element = eT.Element("tag")
            tag_element.attrib["name"] = tag.name
            tag_element.attrib["path"] = tag.path
            act_element.append(tag_element)

    elif act_type == activities.ManualDefinedActivity.ManualDefinedActivity.name:
        act_element.attrib["type"] = activities.ManualDefinedActivity.ManualDefinedActivity.name
        for tag in activity.tags:
            tag_element = eT.Element("tag")
            tag_element.attrib["name"] = tag.name
            tag_element.attrib["text"] = tag.screentext
            tag_element.attrib["finishType"] = tag.finish_type
            tag_element.attrib["time"] = str(tag.time)
            act_element.append(tag_element)

    elif act_type == activities.AssociatedKeyActivity.AssociatedKeyActivity.name:
        act_element.attrib["type"] = activities.AssociatedKeyActivity.AssociatedKeyActivity.name
        for tag in activity.tags:
            tag_element = eT.Element("tag")
            tag_element.attrib["name"] = tag.name
            tag_element.attrib["text"] = tag.screentext
            tag_element.attrib["key"] = tag.key
            act_element.append(tag_element)

    eT.ElementTree(act_element).write(file_path, encoding="UTF-8")


def get_activity_object_from_xml(file_path):
    tree = eT.ElementTree(file=file_path)
    element = tree.getroot()
    activity = None
    if element.attrib["type"] == activities.PhotoPresentation.PhotoPresentation.name:
        tags = []
        for tagelement in element.findall("tag"):
            sounds = []
            for soundElement in tagelement.findall("sound"):
                sound = activities.PhotoPresentation.Sound(soundElement.attrib["path"])
                sounds.append(sound)
            tag = activities.PhotoPresentation.PhotoPresentationTag(
                tagelement.attrib["name"],
                tagelement.attrib["path"],
                tagelement.attrib["associatedSound"],
                sounds
            )

            tags.append(tag)
        activity = activities.PhotoPresentation.PhotoPresentation(
            element.attrib["id"],
            element.attrib["name"],
            element.attrib["random"],
            int(element.attrib["gap"]),
            tags)

    elif element.attrib["type"] == activities.VideoPresentation.VideoPresentation.name:
        tags = []
        for tagelement in element.findall("tag"):
            tag = activities.VideoPresentation.VideoTag(
                tagelement.attrib["name"],
                tagelement.attrib["path"])
            tags.append(tag)
        activity = activities.VideoPresentation.VideoPresentation(
            element.attrib["id"],
            element.attrib["name"],
            element.attrib["random"],
            tags
        )

    elif element.attrib["type"] == activities.SoundPresentation.SoundPresentation.name:
        tags = []
        for tagelement in element.findall("tag"):
            images = []
            for image_element in tagelement.findall("image"):
                image = activities.SoundPresentation.Image(image_element.attrib["path"])
                images.append(image)
            tag = activities.SoundPresentation.SoundPresentationTag(
                tagelement.attrib["name"],
                tagelement.attrib["path"],
                tagelement.attrib["random"],
                tagelement.attrib["associatedImage"],
                images
            )
            tags.append(tag)
        activity = activities.SoundPresentation.SoundPresentation(
            element.attrib["id"],
            element.attrib["name"],
            element.attrib["random"],
            tags
        )

    elif element.attrib["type"] == activities.ManualDefinedActivity.ManualDefinedActivity.name:
        tags = []
        for tag_element in element.findall("tag"):
            tag = activities.ManualDefinedActivity.ManualDefinedTag(
                tag_element.attrib["name"],
                tag_element.attrib["text"],
                tag_element.attrib["finishType"],
                int(tag_element.attrib["time"])
            )
            tags.append(tag)
        activity = activities.ManualDefinedActivity.ManualDefinedActivity(
            element.attrib["id"],
            element.attrib["name"],
            tags
        )

    elif element.attrib["type"] == activities.AssociatedKeyActivity.AssociatedKeyActivity.name:
        tags = []
        for tag_element in element.findall("tag"):
            tag = activities.AssociatedKeyActivity.AssociatedKeyTag(
                tag_element.attrib["name"],
                tag_element.attrib["text"],
                tag_element.attrib["key"]
            )
            tags.append(tag)
        activity = activities.AssociatedKeyActivity.AssociatedKeyActivity(
            element.attrib["id"],
            element.attrib["name"],
            tags
        )
    return activity
