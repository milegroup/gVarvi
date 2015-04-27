# coding=utf-8
__author__ = 'nico'

import pygame
from datetime import datetime
import time

from player.Player import AbstractPlayer
from config import EXIT_SUCCESS_CODE, EXIT_ABORT_CODE
from config import NEXT_TAG_KEY, ABORT_KEY
from config import FRAMERATE


class ManualActivityPlayer(AbstractPlayer):
    def __init__(self, tags):
        self.tags = tags
        self.done = False
        self.ended_tag = False
        self.return_code = None
        self.event_thread = None
        self.zerotime = None

    def play(self, writer):
        self.return_code = EXIT_SUCCESS_CODE

        pygame.init()

        info_object = pygame.display.Info()

        screen_width = info_object.current_w
        screen_height = info_object.current_h
        size = (screen_width, screen_height)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        font = pygame.font.SysFont("arial", 80)
        color = (0, 0, 0)  # Black

        self.zerotime = datetime.now()

        clock = pygame.time.Clock()
        self.zerotime = datetime.now()

        for tag in self.tags:
            beg = (datetime.now() - self.zerotime).total_seconds()
            if tag.finish_type == "Timed":
                start = time.time()
            self.ended_tag = False
            text = font.render(tag.screentext, True, color)
            screen.fill((255, 255, 255))
            screen.blit(text,
                        (screen_width / 2 - text.get_width() // 2, screen_height / 2 - text.get_height() // 2))
            pygame.display.flip()
            while not self.done and not (tag.finish_type == "Timed" and time.time() - start > tag.time) and not (
                            tag.finish_type == "Key (SPACE BAR)" and self.ended_tag):
                for event in pygame.event.get(pygame.KEYDOWN):
                    if event.key == ABORT_KEY:
                        self.done = True
                    elif event.key == NEXT_TAG_KEY:
                        self.ended_tag = True
                clock.tick(FRAMERATE)
            if self.done:
                self.return_code = EXIT_ABORT_CODE
                break
            else:
                end = (datetime.now() - self.zerotime).total_seconds()
                writer.write_tag_value(tag.name, beg, end)
        self._stop()
        self.raise_if_needed(self.return_code)

    def _stop(self):
        self.done = True
        pygame.display.quit()
        pygame.quit()


