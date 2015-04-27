__author__ = 'nico'


# --- General imports for all Players ---

import pygame
from pygame.locals import *
from pygame.compat import unicode_
import sys
import os
from abc import ABCMeta, abstractmethod
import glob
import time
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO