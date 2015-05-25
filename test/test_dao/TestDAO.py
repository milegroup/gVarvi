# coding=utf-8
__author__ = 'nico'

import unittest

from gvarvi.dao.XMLMapper import XMLMapper


class TestDAO(unittest.TestCase):
    def setUp(self):
        with open("activities.xml", "wt") as f:
            f.write(
                """<?xml version='1.0' encoding='UTF-8'?>
<activities>
    <activity gap="5" id="1" name="Photo presentation test activity" random="No" type="Photo presentation">
        <tag name="Tag 1" path="/path/to/tag1photos" associatedSound="Yes">
            <sound path="/path/to/sound_example.wav"/>
        </tag>
        <tag name="Tag 2" path="/path/to/tag2photos" associatedSound="No">
            <sound path="/path/to/sound_example.mp3"/>
        </tag>
    </activity>
    <activity id="2" name="Video presentation test activity" random="Yes" type="Video presentation">
        <tag name="Tag 1" path="/path/to/tag1video"/>
        <tag name="Tag 2" path="/path/to/tag2video"/>
        <tag name="Tag 3" path="/path/to/tag3video"/>
    </activity>
    <activity id="3" name="Sound presentation test activity" random="No" type="Sound presentation">
        <tag associatedImage="Yes" name="Tag 1" path="/path/to/tag1sounds" random="No">
            <image path="/path/to/photo1"/>
            <image path="/path/to/photo2"/>
        </tag>
        <tag associatedImage="No" name="Tag 2" path="/path/to/tag2sounds" random="No"/>
        <tag associatedImage="Yes" name="Tag 3" path="/path/to/tag3sounds" random="No">
            <image path="/path/to/photo3"/>
            <image path="/path/to/photo4"/>
        </tag>
    </activity>
    <activity id="4" name="Associated key test activity" type="Associated-Key tagged activity">
        <tag key="A" name="Tag 1" text="Tag 1 text"/>
        <tag key="B" name="Tag 2" text="Tag 2 text"/>
    </activity>
    <activity id="5" name="Manual defined test activity" type="Manual defined activity">
        <tag finishType="Timed" name="Tag 1" text="Tag 1 text" time="6"/>
        <tag finishType="Key (SPACE BAR)" name="Tag 2" text="Tag 2 text" time="5"/>
    </activity>
</activities>
""")
        with open("conf.xml", "wt") as f:
            f.write("""<?xml version='1.0' encoding='UTF-8'?>
<config>
<defaultMode>Demo mode</defaultMode>
<bluetoothSupport>No</bluetoothSupport>
<antSupport>No</antSupport>
<scanDevicesOnStartup>Yes</scanDevicesOnStartup>
<remoteDebugger>No</remoteDebugger>
<rdIP>10.20.30.40</rdIP>
<rdPort>4444</rdPort>
</config>""")
        self.mapper = XMLMapper("activities.xml", "conf.xml")
        self.mapper.lastId = 5
        self.mapper.used_ids = [1, 2, 3, 4, 5]
