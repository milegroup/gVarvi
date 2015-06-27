# coding=utf-8

from TestDAO import TestDAO


class TestRemoveActivities(TestDAO):
    def setUp(self):
        super(TestRemoveActivities, self).setUp()

    def test_remove_activity(self):
        self.mapper.remove_activity(1)
        with open(self.mapper.act_file, "rt") as f:
            self.assertEqual(f.read(), """<?xml version='1.0' encoding='UTF-8'?>
<activities>
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
    <activity id="5" name="Manual defined test activity" type="Manual defined activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6" />
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5" />
    </activity>
</activities>""")
