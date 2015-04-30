# coding=utf-8
_author__ = 'nico'

import threading
import os
import contextlib
import itertools
import wave
import logging
import wx
import mutagen.mp3
from PIL import Image

from config import EVT_RESULT_ID







# Custom classes
# --------------------------------


class ResultEvent(wx.PyEvent):
    """
    Simple event to carry arbitrary result data.
    :param data: The data to be carried
    """

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class Singleton(type):
    """
    Metaclass that restricts the instantiation of the subclass to one object
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CustomConsoleHandler(logging.StreamHandler):
    """
    Handler that send log to a TextCtrl object
    :param textctrl: The TextCtrl object
    :type textctrl: wx.TextCtrl
    """

    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self)
        self.textctrl = textctrl
        self.formatter = logging.Formatter("%(levelname)s -- %(message)s")

    def emit(self, record):
        """
        Format the message and send it to the TextCtrl
        :param record: The unformatted message
        """
        msg = self.format(record)
        self.textctrl.WriteText(msg + "\n")
        self.flush()


# Custom functions
# --------------------------------

def run_in_thread(fn):
    """
    Function decorator that runs function in a separated thread
    :param fn: The function that wants to be decorated
    :return: A reference to Thread that executes the function
    """

    def _run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t

    return _run


def get_sound_length(sound_path):
    """
    Gets total duration of a sound
    :param sound_path: Absolute path to the sound file
    :type sound_path: str
    :return: Sound duration, in seconds
    """

    def _combinations(string):
        return tuple(map(''.join, itertools.product(*((c.upper(), c.lower()) for c in string))))

    extension = sound_path.split(".")[-1]
    assert isinstance(sound_path, str)
    if extension in _combinations("mp3"):
        return mutagen.mp3.MP3(sound_path).info.length
    elif extension in _combinations("wav"):
        with contextlib.closing(wave.open(sound_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        return duration


def valid_ip(address):
    """
    Checks if an string is an IP
    :param address: The string
    :type address: str
    :return: True if string is an IP address. Otherwise returs False
    """
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if 0 <= b <= 255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False


def hex2bin(a):
    """
    Convert hexadecimal to binary and keep (1 character -> 4 digits) structure
    :param a: The hexadecimal string
    :type a: str
    Ex: convert 8af1 to 1000101011110001
    """

    if len(a) % 2 == 0:
        b = [a[2 * i] + a[2 * i + 1] for i in range(len(a) / 2)]
        c = map(lambda x: "{0:08b}".format(int(x, 16)), b)
        return "".join(c)
    else:
        a = "0" + a
        return hex2bin(a)[4:]


def convert_folder_images_to_jpeg(folder_path):
    # Should be appear all extensions accepted by Pillow library
    extensions_accepted = [".PNG"]
    if os.path.isdir(folder_path):
        for img in os.listdir(folder_path):
            file_name, file_extension = os.path.splitext(img)
            if file_extension.upper() in extensions_accepted and not os.path.isfile(file_name + ".JPG"):
                im = Image.open(os.path.join(folder_path, img))
                im.save(os.path.join(folder_path, file_name + ".JPG"), 'jpeg')

    # Custom exceptions
# ---------------------------------


class HostDownError(Exception):
    """
    Raised on Bluetooth host down error
    """
    pass


class FailedAcquisition(Exception):
    """
    Raised on activity playing error
    """
    pass


class AbortedAcquisition(Exception):
    """
    Raised when the user aborts acquisition
    """
    pass


class MissingFiles(Exception):
    """
    Raised when some of the activity files
    had been removed
    """
    pass


class TimedOutError(Exception):
    """
    Raised when a timeout happens
    """


class NoBand(Exception):
    """
    Raised when band not found
    """
    pass
