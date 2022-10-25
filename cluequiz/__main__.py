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

import pygame
from sys import argv
from pygame.locals import FULLSCREEN, QUIT, KEYDOWN, K_ESCAPE
from cluequiz.game import Game
from cluequiz.screen import Screen

def main():
    pygame.display.init()
    pygame.font.init()
    pygame.mixer.init() # devicename='PULSEAUDIO_DEVICE_DESCRIPTION'
    pygame.display.set_mode((0, 0), FULLSCREEN)
    instance = Game(None if len(argv) < 2 else argv[1])
    screen = Screen(instance)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            else:
                screen.handle(event, instance)
        screen.update(instance)
        pygame.display.flip()

if __name__ == '__main__':
    main()
