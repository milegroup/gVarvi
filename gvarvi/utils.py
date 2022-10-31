# coding=utf-8
import os
import shutil
import tarfile
import sys

__author__ = 'nico'

import threading
import contextlib
import itertools
import wave
import logging
import wx
from random import shuffle

import mutagen.mp3

from config import EVT_RESULT_ID, SUPPORTED_IMG_EXTENSIONS


# Custom classes
# --------------------------------


class ResultEvent(wx.PyEvent):
    """
    Simple event to carry arbitrary result data.
    @param data: The data to be carried
    """

    def __init__(self, data):
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
    @param text_ctrl: The TextCtrl object
    @type text_ctrl: wx.TextCtrl
    """

    def __init__(self, text_ctrl):
        logging.StreamHandler.__init__(self)
        self.text_ctrl = text_ctrl
        self.formatter = logging.Formatter("%(levelname)s -- %(message)s")

    def emit(self, record):
        """
        Format the message and send it to the TextCtrl
        @param record: Unformatted message
        """
        msg = self.format(record)
        self.text_ctrl.WriteText(msg + os.linesep)
        self.flush()


# Custom functions
# --------------------------------

def run_in_thread(fn):
    """
    Function decorator that runs function in a separated thread
    @param fn: The function that wants to be decorated
    @return: A reference to Thread that executes the function
    """

    def _run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t

    return _run


def get_sound_length(sound_path):
    """
    Gets total duration of a sound
    @param sound_path: Absolute path to the sound file
    @type sound_path: str
    @return: Sound duration, in seconds
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


def get_folder_images(folder_path):
    """
    Return a list of paths of all supported images in a giving folder.
    @param folder_path: Folder path.
    @return: A list of all supported images.
    """
    return [os.path.join(folder_path, img) for img in os.listdir(folder_path) if os.path.splitext(img)[1].upper() in
            SUPPORTED_IMG_EXTENSIONS]


def pack_folder_and_remove(folder_path, dst_path):
    with tarfile.open(dst_path, "w") as f:
        f.add(folder_path, arcname="activity_auxiliary_folder")
    shutil.rmtree(folder_path)


def unpack_tar_file_and_remove(tar_path, dst_path):
    with tarfile.open(tar_path, "r") as f:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(f, dst_path)


def valid_ip(address):
    """
    Checks if an string is an IP
    @param address: The string
    @type address: str
    @return: True if string is an IP address. Otherwise returns False
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
    @param a: The hexadecimal string
    @type a: str
    Ex: convert 8af1 to 1000101011110001
    """

    if len(a) % 2 == 0:
        b = [a[2 * i] + a[2 * i + 1] for i in range(len(a) / 2)]
        c = map(lambda x: "{0:08b}".format(int(x, 16)), b)
        return "".join(c)
    else:
        a = "0" + a
        return hex2bin(a)[4:]


def parse_rr_file(rr_file):
    """
    Parses file that contains rr values and return a list with all integer values
    @param rr_file: Path to file
    @return: The list with all rr values converted to integer
    """
    with open(rr_file, "rt") as f:
        rr_values = [int(l) for l in f]
        return rr_values


def parse_tag_file(tag_file):
    """
    Parses file that contains tag values and return a list with all information
    @param tag_file: Path to file
    @return: A list of lists with this structure: [beg_seconds, tag_name, duration_seconds]
    """
    with open(tag_file, "rt") as f:
        tag_list = []
        next(f)  # Skipping header row
        for l in f:
            l = l.split()
            beg_list = map(float, l[0].split(":"))
            beg_seconds = beg_list[0] * 3600 + beg_list[1] * 60 + beg_list[2]
            name = l[1]
            duration_seconds = float(l[2])
            tag_list.append([beg_seconds, name, duration_seconds])
        return tag_list


def cumsum(it):
    """
    Cumulative sum of iterable values
    :param it: Iterable
    """
    total = 0
    for x in it:
        total += x
        yield total


def plot(rr_file, tag_file):
    """
    Paint results of acquisition
    @param rr_file: Path to file that contains rr values
    @param tag_file: Path to file that contains tag values
    """

    import matplotlib.pyplot as plt
    plt.switch_backend("WXAgg")

    colors = ['orange', 'green', 'lightblue', 'grey', 'brown', 'red', 'yellow', 'black', 'magenta', 'purple']
    shuffle(colors)
    rr_values = parse_rr_file(rr_file)
    hr_values = map(lambda rr: 60 / (float(rr) / 1000), rr_values)
    tag_values = parse_tag_file(tag_file)
    x = [x / 1000 for x in cumsum(rr_values)]
    y = hr_values
    plt.plot(x, y)

    for tag in tag_values:
        c = colors.pop()
        plt.axvspan(tag[0], tag[0] + tag[2], facecolor=c, alpha=.8, label=tag[1])

    plt.ylabel('Heart rate (bpm)')
    plt.xlabel('Time (s)')
    plt.title('Acquisition results')
    plt.ylim(ymin=min(min(y) - 10, 40), ymax=max(max(y) + 10, 150))
    plt.legend()
    plt.show()


def set_language(language):
    import gettext
    from config import PROJECT_PATH

    DIR = os.path.join(PROJECT_PATH, "locale")
    APP = "gvarvi"
    gettext.textdomain(APP)
    gettext.bindtextdomain(APP, DIR)

    def get_text(original):
        translated = gettext.translation(APP, DIR, languages=[language], fallback=False).gettext(original)
        properly_encoded = translated.decode('utf-8')
        return properly_encoded

    global _
    _ = get_text


@run_in_thread
def open_file(file_path):
    """
    Open a giving file with default application
    @param file_path: Absolute path to the file
    """
    sysplat = sys.platform
    default_command = {"linux2": "xdg-open",
                       "win32": "start",
                       "darwin": "open"}
    os.system("{0} {1}".format(default_command[sysplat], file_path))


def get_translation():
    return _


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


class TarFileNotValid(Exception):
    """
    Raised on import activity operation when tar file is not valid
    """
    pass
