# coding=utf-8
__author__ = 'nico'

from collections import OrderedDict
from datetime import datetime
import pygame

from player.Player import Player
from config import ABORT_KEY, FINISH_KEY, EXIT_SUCCESS_CODE, EXIT_ABORT_CODE
from config import FRAMERATE
from config import pygame_wx_evt_map


class AssociatedKeyActivityPlayer(Player):
    """
    Player for associated key activities
    @param tags: Tags of actual activity.
    """

    def __init__(self, tags):
        self.dict_tags = OrderedDict()
        for tag in tags:
            self.dict_tags[tag.key] = tag
        self.done = False
        self.normal_finished = False
        self.ended_tag = False
        self.return_code = None
        self.event_thread = None
        self.zerotime = None
        self.previous_tag = None
        self.actual_tag = None

    def play(self, writer):
        """
        Plays activity tags.
        @param writer: Object that write tags info.
        """
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
        self.previous_tag = self.dict_tags.values()[0]
        self.actual_tag = self.previous_tag
        self.zerotime = datetime.now()

        while True:
            beg = (datetime.now() - self.zerotime).total_seconds()
            self.ended_tag = False
            text = font.render(self.actual_tag.screentext, True, color)
            screen.fill((255, 255, 255))
            screen.blit(text,
                        (screen_width / 2 - text.get_width() // 2, screen_height / 2 - text.get_height() // 2))
            pygame.display.flip()
            while not self.ended_tag and not self.done and not self.normal_finished:
                for event in pygame.event.get(pygame.KEYDOWN):
                    if event.key == ABORT_KEY:
                        self.done = True
                    elif event.key == FINISH_KEY:
                        self.normal_finished = True
                    elif pygame_wx_evt_map.get(event.key) in self.dict_tags.keys() and pygame_wx_evt_map.get(
                            event.key) != self.actual_tag.key:
                        self._change_tag(self.dict_tags[pygame_wx_evt_map[event.key]])
                clock.tick(FRAMERATE)
            if self.done:
                self.return_code = EXIT_ABORT_CODE
                break
            elif self.ended_tag:
                end = (datetime.now() - self.zerotime).total_seconds()
                writer.write_tag_value(self.previous_tag.name, beg, end)
            elif self.normal_finished:
                end = (datetime.now() - self.zerotime).total_seconds()
                writer.write_tag_value(self.actual_tag.name, beg, end)
                break
        self.stop()
        self.raise_if_needed(self.return_code)

    def _change_tag(self, tag):
        self.previous_tag = self.actual_tag
        self.actual_tag = tag
        self.ended_tag = True

    def stop(self):
        pygame.display.quit()
        pygame.quit()

