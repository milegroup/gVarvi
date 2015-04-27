# coding=utf-8
__author__ = 'nico'

import os
import pygame
import time
from random import shuffle
import sys
from datetime import datetime

from player.Player import AbstractPlayer
from config import FREQ, BITSIZE, CHANNELS, BUFFER, FRAMERATE
from config import ABORT_KEY, EXIT_SUCCESS_CODE, EXIT_ABORT_CODE, EXIT_FAIL_CODE
from Utils import run_in_thread, get_sound_length
from logger import Logger


class SoundPresentationPlayer(AbstractPlayer):
    def __init__(self, random, tags):
        self.logger = Logger()

        self.random = random
        self.tags = tags
        if self.random == "Yes":
            shuffle(self.tags)
        self.ended_tag = False
        self.done = False
        self.return_code = EXIT_SUCCESS_CODE
        self.image_player_thread = None
        self.event_thread = None

        self.zerotime = None

    def play(self, writer):

        background = (0, 0, 0)
        pygame.init()
        info_object = pygame.display.Info()

        screen_width = info_object.current_w
        screen_height = info_object.current_h
        size = (screen_width, screen_height)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        screen.fill(background)
        pygame.display.flip()

        try:
            pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        except pygame.error, exc:
            print >> sys.stderr, "Could not initialize sound system\n %s" % exc
            return 1

        self.zerotime = datetime.now()

        if self.check(self.tags):
            for tag in self.tags:
                self.ended_tag = False
                self.image_player_thread = None
                if tag.image_associated == "Yes":
                    gap = get_sound_length(tag.path) / len(tag.images)
                    self.image_player_thread = self.play_tag_images([img.path for img in tag.images], gap, size, screen,
                                                                    background)
                try:
                    clock = pygame.time.Clock()
                    pygame.mixer.music.load(tag.path)
                    beg = (datetime.now() - self.zerotime).total_seconds()
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() and not self.done:
                        for event in pygame.event.get(pygame.KEYDOWN):
                            if event.key == ABORT_KEY:
                                self.done = True
                        clock.tick(FRAMERATE)
                    if self.done:
                        self.return_code = EXIT_ABORT_CODE
                except pygame.error, exc:
                    self.logger.exception("Could not play sound file: {0}\n{1}".format(tag.path, exc))
                    self.return_code = EXIT_FAIL_CODE

                self.ended_tag = True
                if self.image_player_thread:
                    self.image_player_thread.join()
                end = (datetime.now() - self.zerotime).total_seconds()
                writer.write_tag_value(tag.name, beg, end)
            print "Tags finished"

        else:
            self.return_code = EXIT_ABORT_CODE
        self._stop()
        self.logger.info("Player return code: {0}".format(self.return_code))
        self.raise_if_needed(self.return_code)

    def _stop(self):
        self.done = True
        if self.image_player_thread:
            self.image_player_thread.join()
        pygame.mixer.stop()
        pygame.mixer.quit()
        pygame.quit()

    def check(self, tags):
        tags_ok = True
        for tag in tags:
            if not os.path.isfile(tag.path):
                self.logger.exception("File not exists: {0}".format(tag.path))
                tags_ok = False
                break
        return tags_ok

    @run_in_thread
    def play_tag_images(self, images, gap, size, screen, background):

        screen_width, screen_height = size
        while not self.ended_tag:
            for img in images:
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
                while time.time() - start < gap and not self.ended_tag and not self.done:
                    clock.tick(FRAMERATE)

                if self.done:
                    break
                elif self.ended_tag:
                    screen.fill(background)
                    pygame.display.flip()
                    break
            if self.done:
                break
