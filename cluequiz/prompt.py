# Clue quiz
# Copyright (C) 2019-2022  Luca Schmid

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
from pygame.locals import K_BACKSPACE, K_DELETE, K_RETURN, KEYDOWN, NUMEVENTS, SRCALPHA, USEREVENT

from cluequiz.style import *

TEXTINPUTREADY = USEREVENT + (42 % (NUMEVENTS-USEREVENT))

class TextPrompt:
    def __init__(self, font, width, label, value='', max_width=None, placeholder='', userdata=None):
        self.visible = False
        self.x, self.y, self.w, self.h, self.left, self.top = (None, None, None, None, None, None)
        self.bg = ( 31,  31,  31)
        self.fg = (255, 255, 255)
        self.fog = None

        self.font = font
        self.width = width
        self.label = label
        self.rndrd_label = self.font.render(self.label, True, self.fg, self.bg)
        self.value = value
        self.max_width = max_width
        self.placeholder = placeholder
        self.userdata = userdata

        self.render_value()

    def render_value(self):
        self.rndrd_value = self.font.render(self.value if len(self.value) > 0 else self.placeholder, True, self.fg, CLUE_COLOR)

    def set_style(self, bg=( 31,  31,  31), fg=(255, 255, 255)):
        self.bg = bg
        self.fg = fg
        self.fog = None
        self.rndrd_label = self.font.render(self.label, True, self.fg, self.bg)

    def set_userdata(self, userdata):
        self.userdata = userdata

    def show(self):
        self.visible = True

    def reset(self):
        self.visible = False
        self.value = ''
        self.render_value()

    def is_visible(self):
        return self.visible

    def handle(self, event):
        if not self.visible:
            return

        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                pygame.event.post(pygame.event.Event(TEXTINPUTREADY, { 'userdata': self.userdata, 'value': self.value }))
                self.reset()
            elif event.key == K_DELETE:
                self.reset()
            elif event.key == K_BACKSPACE:
                self.value = self.value[:-1] if len(self.value) > 0 else ''
                self.render_value()
            elif not self.max_width or self.font.size(self.value + event.unicode)[0] <= self.max_width:
                self.value = self.value + event.unicode
                self.render_value()

    def update(self, display):
        if not self.visible:
            return

        dw, dh = display.get_size()
        linesize = self.font.get_linesize()
        if self.w == None:
            min_width = max(self.width+2*CELL_PADDING, self.rndrd_label.get_width()) + 2 * CELL_PADDING
            self.w = max(dw//2, min_width)
            self.x = (dw-self.w) // 2
            self.left = self.x + (self.w-min_width)//2
        if self.h == None:
            min_height = 3 * linesize + 4 * CELL_PADDING
            self.h = max(dh//2, min_height)
            self.y = (dh-self.h) // 2
            self.top = self.y + (self.h-min_height)//2
        if self.fog == None:
            self.fog = pygame.Surface(display.get_size(), flags=SRCALPHA)
            self.fog.fill(FOG_COLOR)

        display.blit(self.fog, (0, 0))
        display.fill(self.bg, rect=pygame.Rect(self.x, self.y, self.w, self.h))

        display.blit(self.rndrd_label, self.rndrd_label.get_rect(centerx=dw//2).move(0, self.top))
        display.fill(CLUE_COLOR, rect=pygame.Rect(self.left+CELL_PADDING, self.top+2*linesize, self.width+2*CELL_PADDING, linesize+2*CELL_PADDING))

        display.set_clip(pygame.Rect(self.left+2*CELL_PADDING, self.top+2*linesize+CELL_PADDING, self.width, linesize))
        display.blit(self.rndrd_value, self.rndrd_value.get_rect(centerx=dw//2).move(0, self.top+2*linesize+CELL_PADDING))
        display.set_clip(None)
