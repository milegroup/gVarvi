# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, invalid-name
##############################################################################
#
# Copyright (c) 2011, Martín Raúl Villalba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
##############################################################################
#
# Beware s/he who enters: uncommented, non unit-tested,
# don't-fix-it-if-it-ain't-broken kind of threaded code ahead.
#

from __future__ import division, absolute_import, print_function, unicode_literals

from time import sleep, time
from threading import Lock, Thread

from third_party.ant.core.constants import MESSAGE_TX_SYNC
from third_party.ant.core.message import Message, ChannelEventMessage
from third_party.ant.core.exceptions import MessageError


def ProcessBuffer(buffer_):
    messages = []

    while len(buffer_) > 0:
        try:
            msg = Message.decode(buffer_)
            messages.append(msg)
            buffer_ = buffer_[len(msg):]
        except MessageError as err:
            if err.internal is not Message.INCOMPLETE:
                i, length = 1, len(buffer_)
                # move to the next SYNC byte
                while i < length and ord(buffer_[i]) != MESSAGE_TX_SYNC:
                    i += 1
                buffer_ = buffer_[i:]
            else:
                break

    return buffer_, messages


def EventPump(evm):
    buffer_ = b''
    while True:
        with evm.running_lock:
            if not evm.running:
                break

        buffer_ += evm.driver.read(20)
        if len(buffer_) == 0:
            continue
        buffer_, messages = ProcessBuffer(buffer_)

        with evm.callbacks_lock:
            for message in messages:
                for callback in evm.callbacks:
                    try:
                        callback.process(message)
                    except Exception as err:  # pylint: disable=broad-except
                        print(err)
        sleep(0.002)


class EventCallback(object):
    def process(self, msg):
        raise NotImplementedError()


class EventMachineCallback(EventCallback):
    MAX_QUEUE = 25
    WAIT_UNTIL = staticmethod(lambda _, __: None)

    def __init__(self):
        self.messages = []
        self.lock = Lock()

    def process(self, msg):
        with self.lock:
            messages = self.messages
            messages.append(msg)
            MAX_QUEUE = self.MAX_QUEUE
            if len(messages) > MAX_QUEUE:
                self.messages = messages[-MAX_QUEUE:]

    def waitFor(self, foo, timeout=10):  # pylint: disable=blacklisted-name
        messages = self.messages
        basetime = time()
        while time() - basetime < timeout:
            with self.lock:
                for emsg in messages:
                    if self.WAIT_UNTIL(foo, emsg):
                        messages.remove(emsg)
                        return emsg
            sleep(0.002)
        raise MessageError("waiting message timeout")


class AckCallback(EventMachineCallback):
    WAIT_UNTIL = staticmethod(lambda msg, emsg: msg.type == emsg.messageID)

    def process(self, msg):
        if isinstance(msg, ChannelEventMessage):
            super(AckCallback, self).process(msg)


class MsgCallback(EventMachineCallback):
    WAIT_UNTIL = staticmethod(lambda class_, emsg: isinstance(emsg, class_))


class EventMachine(object):
    def __init__(self, driver):
        self.driver = driver
        self.callbacks = set()
        self.eventPump = None
        self.running = False

        self.callbacks_lock = Lock()
        self.running_lock = Lock()

        self.ack = ack = AckCallback()
        self.msg = msg = MsgCallback()
        self.registerCallback(ack)
        self.registerCallback(msg)

    def registerCallback(self, callback):
        with self.callbacks_lock:
            self.callbacks.add(callback)

    def removeCallback(self, callback):
        with self.callbacks_lock:
            try:
                self.callbacks.remove(callback)
            except KeyError:
                pass

    def waitForAck(self, msg):
        channelEventMsg = self.ack.waitFor(msg)
        return channelEventMsg.messageCode

    def waitForMessage(self, class_):
        return self.msg.waitFor(class_)

    def start(self, driver=None):
        with self.running_lock:
            if self.running:
                return
            self.running = True

            if driver is not None:
                self.driver = driver

            evPump = self.eventPump = Thread(target=EventPump, args=(self,))
            evPump.start()

    def stop(self):
        with self.running_lock:
            if not self.running:
                return
            self.running = False
        self.eventPump.join()
