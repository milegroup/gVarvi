# coding=utf-8

import pygame
from datetime import datetime
from random import shuffle

from player.Player import Player
from config import FRAMERATE
from config import ABORT_KEY
from config import EXIT_SUCCESS_CODE, EXIT_ABORT_CODE
from third_party import vlc


class VideoPresentationPlayer(Player):
    """
    Plays a Video presentation activity and listen for keyboard events
    @param random: If is set to "Yes" tags will be played in a random way. It can be set to "Yes" or "No"
    @type random: str
    @param tags: list of VideoPresentationTag objects that contain all tag info.
    @type tags: list
    """

    def __init__(self, random, tags):

        self.tags = tags
        if random == "Yes":
            shuffle(self.tags)
        self.done = False

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        self.return_code = None
        self.zero_time = None

    def play(self, writer):
        import sys
        self.return_code = EXIT_SUCCESS_CODE

        pygame.init()
        info_object = pygame.display.Info()

        screen_width = info_object.current_w
        screen_height = info_object.current_h
        size = (screen_width, screen_height)
        pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        # Pass pygame window id to vlc player, so it can render its contents there.
        win_id = pygame.display.get_wm_info()['window']
        if sys.platform == "linux2":  # for Linux using the X Server
            self.player.set_xwindow(win_id)
        elif sys.platform == "win32":  # for Windows
            self.player.set_hwnd(win_id)
        elif sys.platform == "darwin":  # for MacOS
            self.player.set_agl(win_id)

        self.zero_time = datetime.now()
        for tag in self.tags:
            media = self.Instance.media_new(tag.path)
            self.player.set_media(media)
            beg = (datetime.now() - self.zero_time).total_seconds()
            # Quit pygame mixer to allow vlc full access to audio device (REINIT AFTER MOVIE PLAYBACK IS FINISHED!)
            pygame.mixer.quit()
            self.player.play()
            clock = pygame.time.Clock()
            while self.player.get_state() != vlc.State.Ended and not self.done:
                for event in pygame.event.get(pygame.KEYDOWN):
                    if event.key == ABORT_KEY:
                        self.done = True
                clock.tick(FRAMERATE)
            if self.done:
                self.return_code = EXIT_ABORT_CODE
                break
            end = (datetime.now() - self.zero_time).total_seconds()
            writer.write_tag_value(tag.name, beg, end)
        self.stop()
        self.raise_if_needed(self.return_code)

    def stop(self):
        self.done = True
        self.player.stop()
        pygame.mixer.init()
        pygame.quit()
