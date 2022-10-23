# Clue quiz
# Copyright (C) 2018-2022  Luca Schmid

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

from .config import config
from paho.mqtt.client import Client
from pygame.key import get_pressed
from pygame.locals import K_1, K_2, K_3, K_4
import serial

TOPIC = 'cluequiz/pressed_button'

def open_serial(port, baud):
    try:
        return serial.Serial(port, baud, timeout=0)
    except serial.SerialException:
        return None

class Input:
    def __init__(self):
        self.port = config('serial.port', '/dev/ttyUSB0')
        self.baud = config('serial.baud', 9600)
        self.serial = None

        self.queue = []
        if config('mqtt_input', None):
            certfile = config('mqtt_input.certfile')
            keyfile = config('mqtt_input.keyfile')
            host = config('mqtt_input.host')
            port = config('mqtt_input.port', 8883)

            def on_connect(client, userdata, flags, rc):
                if rc != 0:
                    return

                client.subscribe(TOPIC)

            def on_message(client, userdata, message):
                if message.topic != TOPIC or message.payload not in [b'1', b'2', b'3', b'4']:
                    return

                self.queue.append(message.payload)

            self.client = Client()
            self.client.on_connect = on_connect
            self.client.on_message = on_message
            self.client.tls_set(certfile=certfile, keyfile=keyfile)
            self.client.connect(host, port)
            self.client.loop_start()

    def keep_alive(self):
        if not self.serial:
            self.serial = open_serial(self.port, self.baud)

    def read(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)

        if self.serial:
            try:
                return self.serial.read()
            except serial.SerialException:
                self.serial = None

        pressed = get_pressed()
        if pressed[K_1]:
            return b'1'
        elif pressed[K_2]:
            return b'2'
        elif pressed[K_3]:
            return b'3'
        elif pressed[K_4]:
            return b'4'
        return b''
