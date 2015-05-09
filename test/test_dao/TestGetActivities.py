# coding=utf-8

__author__ = 'nico'

from activities.PhotoPresentation import PhotoPresentation, PhotoPresentationTag
from activities.VideoPresentation import VideoPresentation, VideoTag
from activities.SoundPresentation import SoundPresentation, SoundPresentationTag
from activities.AssociatedKeyActivity import AssociatedKeyActivity, AssociatedKeyTag
from activities.ManualDefinedActivity import ManualDefinedActivity, ManualDefinedTag
from TestDAO import TestDAO


class TestGetActivities(TestDAO):
    def setUp(self):
        super(TestGetActivities, self).setUp()

    def test_read_activities_file(self):
        activities = self.mapper.read_activities_file()
        self.assertEqual(len(activities), 5, "Activities list must have 5 activities")

    def test_get_non_existent_activity(self):
        self.assertRaises(KeyError, self.mapper.get_activity, 100)

    def test_get_photo_presentation_activity(self):
        activity = self.mapper.get_activity(1)
        self.assertIsInstance(activity, PhotoPresentation, "Activity with id 1 must be a Photo presentation activity")
        self.assertEqual(activity.name, "Photo presentation test activity",
                         "Activity name must be 'Photo presentation test activity'")
        self.assertEqual(activity.random, "No", "Activity must not be random")
        self.assertEqual(activity.gap, 5, "Gap must be 5")
        tags = activity.tags
        self.assertEqual(len(tags), 2, "Activity must have 2 tags")
        for t in tags:
            self.assertIsInstance(t, PhotoPresentationTag, "Tag must be a Photo Presentation tag")
        self.assertEqual(tags[0].name, "Tag 1", "Tag name must be 'Tag 1'")
        self.assertEqual(tags[0].path, "/path/to/tag1photos", "Tag path must be '/path/to/tag1photos'")
        self.assertEqual(tags[0].associated_sound, "Yes", "Tag must have 'associatedSound' flag activated")
        self.assertEqual(len(tags[0].sounds), 1, "Tag must have 1 associated sound")
        self.assertEqual(tags[0].sounds[0].path, "/path/to/sound_example.wav", "Sound path must be "
                                                                               "'/path/to/sound_example.wav'")
        self.assertEqual(tags[1].associated_sound, "No", "Tag must not have 'associatedSound' flag activated")

    def test_get_video_presentation_activity(self):
        activity = self.mapper.get_activity(2)
        self.assertIsInstance(activity, VideoPresentation, "Activity with id 2 must be a Video presentation activity")
        self.assertEqual(activity.name, "Video presentation test activity",
                         "Activity name must be 'Video presentation test activity'")
        self.assertEqual(activity.random, "Yes", "Activity must be random")
        tags = activity.tags
        self.assertEqual(len(tags), 3, "Activity must have 3 tags")
        for t in tags:
            self.assertIsInstance(t, VideoTag, "Tag must be a Video tag")
        self.assertEqual(tags[0].name, "Tag 1", "Tag name must be 'Tag 1")
        self.assertEqual(tags[0].path, "/path/to/tag1video", "Tag path must be '/path/to/tag1video'")

    def test_get_sound_presentation_activity(self):
        activity = self.mapper.get_activity(3)
        self.assertIsInstance(activity, SoundPresentation, "Activity with id 3 must be a Sound presentation "
                                                           "activity")
        self.assertEqual(activity.name, "Sound presentation test activity",
                         "Activity name must be 'Sound presentation test activity'")
        self.assertEqual(activity.random, "No", "Activity must not be random")
        tags = activity.tags
        self.assertEqual(len(tags), 3, "Activity must have 3 tags")
        for t in tags:
            self.assertIsInstance(t, SoundPresentationTag, "Tag must be a Sound presentation tag")
        self.assertEqual(tags[0].name, "Tag 1", "Tag name must be 'Tag 1")
        self.assertEqual(tags[0].path, "/path/to/tag1sounds", "Tag path must be '/path/to/tag1sounds'")
        self.assertEqual(tags[0].associated_image, "Yes", "Tag must have 'associatedImage' flag activated")
        imgs = tags[0].images
        self.assertEqual(len(imgs), 2, "Tag must have 2 associated images")
        self.assertEqual(imgs[0].path, "/path/to/photo1", "Associated image path must be '/path/to/photo1'")

    def test_get_associated_key_activity(self):
        activity = self.mapper.get_activity(4)
        self.assertIsInstance(activity, AssociatedKeyActivity, "Activity with id 4 must be an Associated key "
                                                               "activity ")
        self.assertEqual(activity.name, "Associated key test activity",
                         "Activity name must be 'Associated key test activity'")
        tags = activity.tags
        self.assertEqual(len(tags), 2, "Activity must have 2 tags")
        for t in tags:
            self.assertIsInstance(t, AssociatedKeyTag, "Tag must be an Associated key tag")
        self.assertEqual(tags[0].name, "Tag 1", "Tag name must be 'Tag 1'")
        self.assertEqual(tags[0].key, "A", "Tag key must be 'A'")
        self.assertEqual(tags[0].screentext, "Tag 1 text", "Tag screen text must be 'Tag 1 text'")

    def test_get_manual_defined_activity(self):
        activity = self.mapper.get_activity(5)
        self.assertIsInstance(activity, ManualDefinedActivity, "Activity with id 5 must be an Manual defined "
                                                               "activity ")
        self.assertEqual(activity.name, "Manual defined test activity",
                         "Activity name must be 'Manual defined test activity'")
        tags = activity.tags
        self.assertEqual(len(tags), 2, "Activity must have 2 tags")
        for t in tags:
            self.assertIsInstance(t, ManualDefinedTag, "Tag must be an Associated key tag")
        self.assertEqual(tags[0].name, "Tag 1", "Tag name must be 'Tag 1'")
        self.assertEqual(tags[0].finish_type, "Timed", "Tag finish type must be 'Timed'")
        self.assertEqual(tags[0].time, 6, "Tag time must be 6")
        self.assertEqual(tags[0].screentext, "Tag 1 text", "Tag screen text must be 'Tag 1 text'")
        self.assertEqual(tags[1].finish_type, "Key (SPACE BAR)")