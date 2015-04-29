# coding=utf-8
__author__ = 'nico'

from random import shuffle
from datetime import datetime

import pygame
from pygame.locals import Rect

from player.Player import Player
from config import FRAMERATE
from config import ABORT_KEY
from config import EXIT_SUCCESS_CODE, EXIT_ABORT_CODE


class VideoPresentationPlayer(Player):
    def __init__(self, random, tags):
        self.random = random
        self.tags = tags
        if self.random == "Yes":
            shuffle(self.tags)
        self.done = False
        self.return_code = EXIT_SUCCESS_CODE
        self.event_thread = None
        self.movie = None

        self.zerotime = None

    def play(self, writer):
        pygame.init()
        pygame.mixer.quit()
        pygame.display.init()

        info_display = pygame.display.Info()
        screen_width = info_display.current_w
        screen_height = info_display.current_h
        size = (screen_width, screen_height)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        self.zerotime = datetime.now()

        for tag in self.tags:

            movie = pygame.movie.Movie(tag.path)
            movie.set_display(screen, Rect((5, 5), size))
            beg = (datetime.now() - self.zerotime).total_seconds()
            movie.play()

            clock = pygame.time.Clock()
            while movie.get_busy() and not self.done:
                for event in pygame.event.get(pygame.KEYDOWN):
                    if event.key == ABORT_KEY:
                        movie.stop()
                        self.done = True
                clock.tick(FRAMERATE)

            if self.done:
                self._stop()
                self.return_code = EXIT_ABORT_CODE
                break

            end = (datetime.now() - self.zerotime).total_seconds()
            writer.write_tag_value(tag.name, beg, end)

        self._stop()
        self.raise_if_needed(self.return_code)

    def _stop(self):
        self.done = True
        pygame.quit()


