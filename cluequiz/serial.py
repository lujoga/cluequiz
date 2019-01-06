# Clue quiz
# Copyright (C) 2018-2019  Luca Schmid

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

import serial
from pygame.key import get_pressed
from pygame.locals import K_1, K_2, K_3, K_4

def open_serial(port, baud):
    try:
        return serial.Serial(port, baud, timeout=0)
    except serial.SerialException:
        return None

class Serial:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = open_serial(port, baud)

    def keep_alive(self):
        if not self.serial:
            self.serial = open_serial(self.port, self.baud)

    def read(self):
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
