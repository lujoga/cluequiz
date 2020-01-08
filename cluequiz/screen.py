# Clue quiz
# Copyright (C) 2018-2020  Luca Schmid

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
from pygame.locals import (
    K_BACKSPACE,
    K_DELETE,
    KEYDOWN,
    K_1,
    K_2,
    K_3,
    K_4,
    K_f,
    K_j,
    K_n,
    K_u,
    MOUSEBUTTONDOWN,
    SRCALPHA,
)
from PIL import Image
from yaml import load
from os.path import dirname, join
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from io import BytesIO

from cluequiz.serial import Serial
from cluequiz.style import *
from cluequiz.config import config
from cluequiz.prompt import TEXTINPUTREADY, TextPrompt

CHOOSING = 0
DISPLAY_CLUE = 1
RESPONDING = 2
DISPLAY_QUESTION = 3
SCOREBOARD = 4

class Screen:
    def __init__(self, instance):
        self.serial = Serial(config('serial.port', '/dev/ttyUSB0'), config('serial.baud', 9600))

        screen_size = pygame.display.get_surface().get_size()
        if config.debug:
            screen_size = (800, 600)

        self.screen_w = screen_size[0] - (screen_size[0] % 12)
        cell_w = screen_size[0] // 12
        self.clue_w = cell_w * 2
        self.score_w = cell_w * 3
        half_cell_h = screen_size[1] // 14
        self.cell_h = half_cell_h * 2
        self.score_h = half_cell_h * 7
        self.padding = ((screen_size[0] % 12) // 2, (screen_size[1] % 14) // 2)

        self.font = pygame.font.Font(None, FONT_SIZE)
        self.bigfont = pygame.font.Font(None, BIGFONT_SIZE)

        self.values = []
        for i in range(1, 6):
            self.values.append(self.font.render(str(i*100), True, TEXT_COLOR, CLUE_COLOR))
        self.scores = [ None, None, None, None ]
        self.render_score(None, instance)
        self.names = [ None, None, None, None ]
        self.render_name(None, instance)

        self.load_clue_set(instance.next_clue_set())

        self.prompt = TextPrompt(self.font, self.score_w, 'Player name', max_width=self.score_w, placeholder='Hier könnte dein Name stehen')

        self.state = CHOOSING

    def read_serial(self):
        b = self.serial.read()
        if len(b) > 0:
            i = b[0] - 49
            if i >= 0 and i < 4:
                return i
        return None

    def empty_serial(self):
        b = self.serial.read()
        while len(b) > 0:
            b = self.serial.read()

    def load_image(self, name, bg):
        try:
            im = Image.open(name)
        except IOError as msg:
            print('Could not load image ', name)
            raise SystemExit(msg)

        w, h = im.size
        if w > self.screen_w:
            w = self.screen_w
        if h > self.cell_h*6:
            h = self.cell_h * 6
        im.thumbnail((w, h))

        if config.debug:
            print(name, im.mode)

        image = pygame.image.fromstring(im.tobytes('raw', im.mode), im.size, im.mode)
        image.convert()

        if bg:
            image_bg = pygame.Surface(im.size)
            image_bg.fill(bg)
            image_bg.blit(image, (0, 0))
            return image_bg

        return image

    def render_code(self, code, lang):
        formatter = ImageFormatter(font_size=FONT_SIZE, line_numbers=False, style=CODE_STYLE)
        image = pygame.image.load(BytesIO(highlight(code, get_lexer_by_name(lang), formatter)), 'code.png')
        image.convert()
        return image

    def render_wrapped(self, text, font, color, line_w):
        lines = []
        space_left = 0
        space_width = font.size(' ')[0]
        for w in text.split():
            width = font.size(w)[0]
            if (space_width + width) > space_left:
                lines.append(w)
                space_left = line_w - width
            else:
                lines[-1] = lines[-1] + ' ' + w
                space_left = space_left - (space_width + width)

        line_h = font.get_linesize()
        target = pygame.Surface((line_w, len(lines)*line_h), flags=SRCALPHA)
        for i, l in enumerate(lines):
            line = font.render(l, True, color)
            target.blit(line, line.get_rect(centerx=line_w*0.5, centery=line_h*(i+0.5)))
        return target

    def load_clue_set(self, yml):
        with open(yml, 'r') as f:
            clue_set = load(f)

        self.categories = []
        self.clues = [ [], [], [], [], [], [] ]
        self.questions = [ [], [], [], [], [], [] ]
        for category, clues in clue_set.items():
            if len(clues) != 5:
                raise ValueError('A valid category has exactly five clues')
            for o in clues:
                i = len(self.categories)
                if 'image' in o:
                    bg = None if 'bg' not in o else o['bg']
                    self.clues[i].append(self.load_image(join(dirname(yml), o['image']), bg))
                elif 'clue' in o:
                    if 'lang' in o:
                        self.clues[i].append(self.render_code(o['clue'], o['lang']))
                    else:
                        self.clues[i].append(self.render_wrapped(o['clue'], self.bigfont, TEXT_COLOR, self.screen_w))
                else:
                    raise ValueError('Clue has neither text nor image')
                self.questions[i].append(self.render_wrapped(str(o['question']), self.bigfont, TEXT_COLOR, self.screen_w))
            self.categories.append(self.render_wrapped(category, self.font, TEXT_COLOR, self.clue_w))

        if len(self.categories) != 6:
            raise ValueError('A valid clue set has exactly six categories')

    def render_score(self, player, instance):
        """Render a specific or all player's scores."""
        if player is None:
            for player in range(4):
                self.render_score(player, instance)
        else:
            self.scores[player] = self.font.render(str(instance.get_score(player)), True, TEXT_COLOR)

    def render_name(self, player, instance):
        if player == None:
            for player in range(4):
                self.render_name(player, instance)
        else:
            self.names[player] = self.font.render(instance.get_name(player), True, TEXT_COLOR)

    def offset_rect(self, x, y, w, h):
        return pygame.Rect(self.padding[0] + x, self.padding[1] + y, w, h)

    def pad_rect(self, x, y, w, h, p):
        return pygame.Rect(self.padding[0]+p+x, self.padding[1]+p+y, w-2*p, h-2*p)

    def handle(self, event, instance):
        if self.prompt.is_visible():
            self.prompt.handle(event)
            return

        if event.type == KEYDOWN:
            if event.key == K_f:
                pygame.display.toggle_fullscreen()
            elif event.key == K_u:
                instance.rollback(1)
                self.render_score(None, instance)
        elif event.type == TEXTINPUTREADY:
            if event.userdata != None:
                instance.set_name(event.userdata, event.value)
                self.render_name(event.userdata, instance)

        if self.state == CHOOSING:
            if event.type == MOUSEBUTTONDOWN:
                x = (event.pos[0] - self.padding[0]) // self.clue_w
                y = (event.pos[1] - self.padding[1]) // self.cell_h - 1
                if x >= 0 and x < 6 and y >= 0 and y < 5 and instance.get_state_at(x, y) == None:
                    instance.set_selected(x, y)
                    self.state = DISPLAY_QUESTION if config.viewer else DISPLAY_CLUE
                    self.empty_serial()
            elif event.type == KEYDOWN:
                if event.key == K_DELETE:
                    instance.clear()
                    self.render_score(None, instance)
                    self.load_clue_set(instance.next_clue_set())
                elif event.key == K_1:
                    self.prompt.set_style(PLAYERS[0])
                    self.prompt.set_userdata(0)
                    self.prompt.show()
                elif event.key == K_2:
                    self.prompt.set_style(PLAYERS[1])
                    self.prompt.set_userdata(1)
                    self.prompt.show()
                elif event.key == K_3:
                    self.prompt.set_style(PLAYERS[2])
                    self.prompt.set_userdata(2)
                    self.prompt.show()
                elif event.key == K_4:
                    self.prompt.set_style(PLAYERS[3])
                    self.prompt.set_userdata(3)
                    self.prompt.show()
        elif self.state == DISPLAY_CLUE:
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    instance.clear_responded()
                    self.state = CHOOSING
                elif event.key == K_DELETE:
                    instance.ignore_clue()
                    instance.clear_responded()
                    self.state = DISPLAY_QUESTION
        elif self.state == RESPONDING:
            if event.type == KEYDOWN:
                if event.key == K_j:
                    instance.correct()
                    instance.clear_responded()
                    self.render_score(instance.get_responding(), instance)
                    self.state = DISPLAY_QUESTION
                elif event.key == K_n:
                    instance.wrong()
                    self.render_score(instance.get_responding(), instance)
                    if instance.all_responded():
                        instance.ignore_clue()
                        instance.clear_responded()
                        self.state = DISPLAY_QUESTION
                    else:
                        self.state = DISPLAY_CLUE
                        self.empty_serial()
        elif self.state == DISPLAY_QUESTION:
            if event.type == KEYDOWN:
                if instance.finished():
                    for i in range(4):
                        self.scores[i] = self.bigfont.render(str(instance.get_score(i)), True, TEXT_COLOR, PLAYERS[i])
                        self.names[i] = self.bigfont.render(instance.get_name(i), True, TEXT_COLOR, PLAYERS[i])
                    self.state = SCOREBOARD
                else:
                    self.state = CHOOSING
        elif self.state == SCOREBOARD:
            if event.type == KEYDOWN:
                instance.clear()
                self.render_score(None, instance)
                self.render_name(None, instance)
                self.load_clue_set(instance.next_clue_set())
                self.state = CHOOSING

    def update(self, instance):
        self.serial.keep_alive()
        if self.state == DISPLAY_CLUE:
            i = self.read_serial()
            if i != None and instance.set_responding(i):
                self.state = RESPONDING

        display = pygame.display.get_surface()
        display.fill(BACKGROUND if self.state != RESPONDING else PLAYERS[instance.get_responding()])

        px, py = self.padding

        if self.state == CHOOSING:
            for i, c in enumerate(self.categories):
                display.blit(c, c.get_rect(centerx=px+self.clue_w*(i+0.5), centery=py+self.cell_h*0.5))
            for j in range(5):
                v = self.values[j]
                for i in range(6):
                    s = instance.get_state_at(i, j)
                    if s == None:
                        display.fill(CLUE_COLOR, rect=self.pad_rect(self.clue_w*i, self.cell_h*(j+1), self.clue_w, self.cell_h, CELL_PADDING))
                        display.blit(v, v.get_rect(centerx=px+self.clue_w*(i+0.5), centery=py+self.cell_h*(j+1.5)))
                    elif s >= 0:
                        display.fill(PLAYERS[s], rect=self.pad_rect(self.clue_w*i, self.cell_h*(j+1), self.clue_w, self.cell_h, CELL_PADDING))
        elif self.state == SCOREBOARD:
            display.fill(PLAYERS[0], rect=self.offset_rect(0,              0,            self.score_w*2, self.score_h))
            display.fill(PLAYERS[1], rect=self.offset_rect(self.score_w*2, 0,            self.score_w*2, self.score_h))
            display.fill(PLAYERS[2], rect=self.offset_rect(0,              self.score_h, self.score_w*2, self.score_h))
            display.fill(PLAYERS[3], rect=self.offset_rect(self.score_w*2, self.score_h, self.score_w*2, self.score_h))
            display.blit(self.scores[0], self.scores[0].get_rect(centerx=px+self.score_w,   centery=py+self.score_h*0.5))
            display.blit(self.scores[1], self.scores[1].get_rect(centerx=px+self.score_w*3, centery=py+self.score_h*0.5))
            display.blit(self.scores[2], self.scores[2].get_rect(centerx=px+self.score_w,   centery=py+self.score_h*1.5))
            display.blit(self.scores[3], self.scores[3].get_rect(centerx=px+self.score_w*3, centery=py+self.score_h*1.5))
            display.blit(self.names[0], self.names[0].get_rect(centerx=px+self.score_w).move(0, py+self.score_h-(self.bigfont.get_linesize()+CELL_PADDING)))
            display.blit(self.names[1], self.names[1].get_rect(centerx=px+self.score_w*3).move(0, py+self.score_h-(self.bigfont.get_linesize()+CELL_PADDING)))
            display.blit(self.names[2], self.names[2].get_rect(centerx=px+self.score_w).move(0, py+self.score_h*2-(self.bigfont.get_linesize()+CELL_PADDING)))
            display.blit(self.names[3], self.names[3].get_rect(centerx=px+self.score_w*3).move(0, py+self.score_h*2-(self.bigfont.get_linesize()+CELL_PADDING)))
        else:
            x, y = instance.get_selected()
            if self.state == DISPLAY_QUESTION:
                s = self.questions[x][y]
            else:
                s = self.clues[x][y]
            display.blit(s, s.get_rect(centerx=px+self.clue_w*3, centery=py+self.cell_h*3))

        if self.state != SCOREBOARD:
            for i in range(4):
                display.fill(PLAYERS[i], rect=self.offset_rect(self.score_w*i, self.cell_h*6, self.score_w, self.cell_h))
                if self.state == CHOOSING and i == instance.get_choosing():
                    display.fill(BACKGROUND, rect=self.pad_rect(self.score_w*i, self.cell_h*6, self.score_w, self.cell_h, CELL_PADDING))
                display.blit(self.scores[i], self.scores[i].get_rect(centerx=px+self.score_w*(i+0.5), centery=py+self.cell_h*6.5))
                display.blit(self.names[i], self.names[i].get_rect(centerx=px+self.score_w*(i+0.5)).move(0, py+self.cell_h*7-(self.font.get_linesize()+CELL_PADDING)))

        self.prompt.update(display)
