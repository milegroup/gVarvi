# coding=utf-8

import time
from random import shuffle
from collections import OrderedDict
from datetime import datetime
import pygame

from player.Player import Player
from config import FREQ, BITSIZE, CHANNELS, BUFFER, FRAMERATE
from config import ABORT_KEY, EXIT_SUCCESS_CODE, EXIT_ABORT_CODE
from utils import run_in_thread, get_folder_images, MissingFiles
from logger import Logger


class PhotoPresentationPlayer(Player):
    """
    Plays a Photo presentation activity and listen for keyboard events
    @param gap: Duration of each picture (in seconds)
    @type gap: int
    @param random: If is set to "Yes" tags will be played in a random way. It can be set to "Yes" or "No"
    @type random: str
    @param tags: list of PhotoPresentationTag objects that contain all tag info.
    @type tags: list
    """

    def __init__(self, gap, random, tags):
        self.logger = Logger()

        self.gap = gap
        self.tags = tags
        if random == "Yes":
            shuffle(self.tags)
        self.ended_tag = False
        self.done = False
        self.return_code = None
        self.sound_player_thread = None
        self.event_thread = None
        self.images = OrderedDict()
        self.zero_time = None

    def play(self, writer):
        """
        Plays activity tags.
        @param writer: Object that write tags info.
        """

        self.return_code = EXIT_SUCCESS_CODE

        try:
            for tag in self.tags:
                images = get_folder_images(tag.path)
                shuffle(images)
                self.images[tag] = images
        except OSError:
            raise MissingFiles()

        background = (0, 0, 0)
        pygame.init()
        info_object = pygame.display.Info()

        screen_width = info_object.current_w
        screen_height = info_object.current_h
        size = (screen_width, screen_height)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        self.zero_time = datetime.now()

        for tag in self.tags:
            self.ended_tag = False
            self.sound_player_thread = None
            if tag.associated_sound == "Yes":
                self.sound_player_thread = self.play_tag_sounds([sound.path for sound in tag.sounds])
            beg = (datetime.now() - self.zero_time).total_seconds()
            for img in self.images[tag]:
                start = time.time()
                img = pygame.image.load(img).convert()
                factor = min((1.0 * screen_width / img.get_width()), (1.0 * screen_height / img.get_height()))
                new_width = int(img.get_width() * factor)
                new_height = int(img.get_height() * factor)
                img = pygame.transform.scale(img, (new_width, new_height))
                screen.fill(background)
                screen.blit(img, ((screen_width - img.get_width()) / 2, ((screen_height - img.get_height()) / 2)))
                pygame.display.flip()
                clock = pygame.time.Clock()
                while time.time() - start < self.gap and not self.done:
                    for event in pygame.event.get(pygame.KEYDOWN):
                        if event.key == ABORT_KEY:
                            self.done = True
                    clock.tick(FRAMERATE)
                if self.done:
                    self.return_code = EXIT_ABORT_CODE
                    break
            self.ended_tag = True
            if self.sound_player_thread:
                self.sound_player_thread.join()
            if self.done:
                end = (datetime.now() - self.zero_time).total_seconds()
                writer.write_tag_value(tag.name, beg, end)
                break
            end = (datetime.now() - self.zero_time).total_seconds()
            writer.write_tag_value(tag.name, beg, end)
        self.stop()
        self.raise_if_needed(self.return_code)

    def stop(self):
        self.done = True
        if self.sound_player_thread:
            self.sound_player_thread.join()
        pygame.quit()

    @run_in_thread
    def play_tag_sounds(self, sounds):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # If sounds playing ends
        # but tag playing goes on,
        # sounds will be played again
        while not self.ended_tag:
            for sound in sounds:
                try:
                    clock = pygame.time.Clock()
                    pygame.mixer.music.load(sound)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() and not self.ended_tag and not self.done:
                        clock.tick(FRAMERATE)
                    if self.ended_tag or self.done:
                        pygame.mixer.music.stop()
                        return
                except pygame.error, exc:
                    self.logger.error("Could not play sound file: {0}".format(sound))
                    self.logger.exception(exc)
