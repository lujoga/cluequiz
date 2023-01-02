#!/usr/bin/env python3
# Clue quiz
# Copyright (C) 2018-2023  Luca Schmid

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from argparse import ArgumentParser
from paho.mqtt.client import Client
from signal import SIGINT, signal
from time import sleep
import serial

TOPIC = 'cluequiz/pressed_button'

class Serial:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud

        self.serial = None
        self.terminated = False

    def open(self):
        if self.serial:
            return

        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=0)
        except serial.SerialException:
            pass

    def read(self):
        self.open()

        while not self.terminated:
            if not self.serial:
                sleep(200)
                self.open()

            try:
                b = self.serial.read()
            except serial.SerialException:
                self.serial = None
                continue

            if len(b) == 0:
                continue

            yield b

    def terminate(self):
        self.terminated = True
        try:
            self.serial.close()
        except:
            pass

def main():
    parser = ArgumentParser()
    parser.add_argument('-b', '--baud', default=9600, help='serial baud rate', type=int)
    parser.add_argument('-d', '--dev', default='/dev/ttyUSB0', help='path to serial device')
    parser.add_argument('-p', '--port', default=8883, help='mqtt port', type=int)
    parser.add_argument('certfile', help='path to client certificate')
    parser.add_argument('keyfile', help='path to private key')
    parser.add_argument('host', help='mqtt host')
    args = parser.parse_args()

    c = Client()
    c.tls_set(certfile=args.certfile, keyfile=args.keyfile)
    c.connect(args.host, args.port)
    c.loop_start()

    s = Serial(args.dev, args.baud)

    terminate = False

    def signal_handler():
        terminate = True

        c.disconnect()
        s.terminate()

    signal(SIGINT, signal_handler)

    for b in s.read():
        if terminate:
            break

        match b:
            case b'1':
                button = '1'
            case b'2':
                button = '2'
            case b'3':
                button = '3'
            case b'4':
                button = '4'
            case _:
                continue

        retry = True
        backoff = 200
        while retry and not terminate:
            try:
                c.publish(TOPIC, button).wait_for_publish()
                retry = False
            except:
                sleep(backoff)
                backoff *= 2

if __name__ == '__main__':
    main()
