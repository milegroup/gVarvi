# coding=utf-8

from activities.PhotoPresentation import PhotoPresentation, PhotoPresentationTag, Sound
from activities.VideoPresentation import VideoPresentation, VideoTag
from activities.SoundPresentation import SoundPresentation, SoundPresentationTag, Image
from activities.AssociatedKeyActivity import AssociatedKeyActivity, AssociatedKeyTag
from activities.ManualDefinedActivity import ManualDefinedActivity, ManualDefinedTag
from TestDAO import TestDAO


class TestSaveActivities(TestDAO):
    def setUp(self):
        super(TestSaveActivities, self).setUp()

    def test_save_photo_presentation_activity(self):
        tag1 = PhotoPresentationTag("Tag 1", "/path/to/tag1", "Yes", [Sound("/path/to/sound1")])
        tag2 = PhotoPresentationTag("Tag 2", "/path/to/tag2", "No")
        tags = [tag1, tag2]
        activity = PhotoPresentation(-1, "Photo presentation test activity", "Yes", 5, tags)
        self.mapper.save_activity(activity)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1photos">
            <sound path="/path/to/sound_example.wav" />
        </tag>
        <tag associatedSound="No" name="Tag 2" path="/path/to/tag2photos">
            <sound path="/path/to/sound_example.mp3" />
        </tag>
    </activity>
    <activity id="2" name="Video presentation test activity" random="Yes" type="Video presentation">
        <tag name="Tag 1" path="/path/to/tag1video" />
        <tag name="Tag 2" path="/path/to/tag2video" />
        <tag name="Tag 3" path="/path/to/tag3video" />
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1" />
            <image path="/path/to/photo2" />
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No" />
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3" />
            <image path="/path/to/photo4" />
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text" />
        <tag key="B" name="Tag 2" text="Tag 2 text" />
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual-defined tagged activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
<activity gap="5" id="6" name="Photo presentation test activity" random="Yes" type="Photo presentation"><tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1"><sound path="/path/to/sound1" /></tag><tag associatedSound="No" name="Tag 2" path="/path/to/tag2" /></activity></activities>""")

    def test_save_video_presentation_activity(self):
        tags = [VideoTag("Tag 1", "/path/to/tag1")]
        activity = VideoPresentation(-1, "Video presentation test activity", "Yes", tags)
        self.mapper.save_activity(activity)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1photos">
            <sound path="/path/to/sound_example.wav" />
        </tag>
        <tag associatedSound="No" name="Tag 2" path="/path/to/tag2photos">
            <sound path="/path/to/sound_example.mp3" />
        </tag>
    </activity>
    <activity id="2" name="Video presentation test activity" random="Yes" type="Video presentation">
        <tag name="Tag 1" path="/path/to/tag1video" />
        <tag name="Tag 2" path="/path/to/tag2video" />
        <tag name="Tag 3" path="/path/to/tag3video" />
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1" />
            <image path="/path/to/photo2" />
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No" />
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3" />
            <image path="/path/to/photo4" />
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text" />
        <tag key="B" name="Tag 2" text="Tag 2 text" />
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual-defined tagged activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
<activity id="6" name="Video presentation test activity" random="Yes" type="Video presentation"><tag name="Tag 1" path="/path/to/tag1" /></activity></activities>""")

    def test_save_sound_presentation_activity(self):
        tag1 = SoundPresentationTag("Tag 1", "/path/to/tag1", "No", "Yes", [Image("/path/to/some/image1"),
                                                                            Image("/path/to/some/image2")])
        tag2 = SoundPresentationTag("Tag 2", "/path/to/tag2", "Yes")
        tags = [tag1, tag2]
        activity = SoundPresentation(-1, "Sound presentation test activity", "Yes", tags)
        self.mapper.save_activity(activity)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1photos">
            <sound path="/path/to/sound_example.wav" />
        </tag>
        <tag associatedSound="No" name="Tag 2" path="/path/to/tag2photos">
            <sound path="/path/to/sound_example.mp3" />
        </tag>
    </activity>
    <activity id="2" name="Video presentation test activity" random="Yes" type="Video presentation">
        <tag name="Tag 1" path="/path/to/tag1video" />
        <tag name="Tag 2" path="/path/to/tag2video" />
        <tag name="Tag 3" path="/path/to/tag3video" />
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1" />
            <image path="/path/to/photo2" />
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No" />
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3" />
            <image path="/path/to/photo4" />
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text" />
        <tag key="B" name="Tag 2" text="Tag 2 text" />
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual-defined tagged activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
<activity id="6" name="Sound presentation test activity" random="Yes" type="Sound presentation"><tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1" random="No"><image path="/path/to/some/image1" /><image path="/path/to/some/image2" /></tag><tag associatedImage="No" name="Tag 2" path="/path/to/tag2" random="Yes" /></activity></activities>""")

    def test_save_associated_key_activity(self):
        tags = [AssociatedKeyTag("Tag1", "Some text 1", "A"), AssociatedKeyTag("Tag 2", "Some text 2", "B")]
        activity = AssociatedKeyActivity(-1, "Video presentation test activity", tags)
        self.mapper.save_activity(activity)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1photos">
            <sound path="/path/to/sound_example.wav" />
        </tag>
        <tag associatedSound="No" name="Tag 2" path="/path/to/tag2photos">
            <sound path="/path/to/sound_example.mp3" />
        </tag>
    </activity>
    <activity id="2" name="Video presentation test activity" random="Yes" type="Video presentation">
        <tag name="Tag 1" path="/path/to/tag1video" />
        <tag name="Tag 2" path="/path/to/tag2video" />
        <tag name="Tag 3" path="/path/to/tag3video" />
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1" />
            <image path="/path/to/photo2" />
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No" />
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3" />
            <image path="/path/to/photo4" />
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text" />
        <tag key="B" name="Tag 2" text="Tag 2 text" />
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual-defined tagged activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
<activity id="6" name="Video presentation test activity" type="Associated-Key tagged activity"><tag key="A" name="Tag1" text="Some text 1" /><tag key="B" name="Tag 2" text="Some text 2" /></activity></activities>""")

    def test_save_manual_defined_activity(self):
        tags = [ManualDefinedTag("Tag1", "Some text 1", "Timed", 6), ManualDefinedTag("Tag 2", "Some text 2",
                                                                                      "Key (SPACE BAR)", 5)]
        activity = ManualDefinedActivity(-1, "Video presentation test activity", tags)
        self.mapper.save_activity(activity)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1photos">
            <sound path="/path/to/sound_example.wav" />
        </tag>
        <tag associatedSound="No" name="Tag 2" path="/path/to/tag2photos">
            <sound path="/path/to/sound_example.mp3" />
        </tag>
    </activity>
    <activity id="2" name="Video presentation test activity" random="Yes" type="Video presentation">
        <tag name="Tag 1" path="/path/to/tag1video" />
        <tag name="Tag 2" path="/path/to/tag2video" />
        <tag name="Tag 3" path="/path/to/tag3video" />
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1" />
            <image path="/path/to/photo2" />
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No" />
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3" />
            <image path="/path/to/photo4" />
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text" />
        <tag key="B" name="Tag 2" text="Tag 2 text" />
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual-defined tagged activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
<activity id="6" name="Video presentation test activity" type="Manual-defined tagged activity"><tag finishType="Timed" name="Tag1" text="Some text 1" time="6" /><tag finishType="Key (SPACE BAR)" name="Tag 2" text="Some text 2" time="5" /></activity></activities>""")

    def test_update_activity(self):
        # Activity after get it from xml
        tags = [VideoTag("Tag 1", "/path/to/tag1video"),
                VideoTag("Tag 2", "/path/to/tag2video"),
                VideoTag("Tag 3", "/path/to/tag3video")]
        activity = VideoPresentation(2, "Video presentation test activity", "Yes", tags)
        # Modifying activity
        activity.name = "Fake name"
        self.mapper.update_activity(2, activity)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag associatedSound="Yes" name="Tag 1" path="/path/to/tag1photos">
            <sound path="/path/to/sound_example.wav" />
        </tag>
        <tag associatedSound="No" name="Tag 2" path="/path/to/tag2photos">
            <sound path="/path/to/sound_example.mp3" />
        </tag>
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1" />
            <image path="/path/to/photo2" />
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No" />
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3" />
            <image path="/path/to/photo4" />
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text" />
        <tag key="B" name="Tag 2" text="Tag 2 text" />
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual-defined tagged activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
<activity id="2" name="Fake name" random="Yes" type="Video presentation"><tag name="Tag 1" path="/path/to/tag1video" /><tag name="Tag 2" path="/path/to/tag2video" /><tag name="Tag 3" path="/path/to/tag3video" /></activity></activities>""")