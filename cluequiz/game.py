# Clue quiz
# Copyright (C) 2018  Luca Schmid

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

from copy import deepcopy
from yaml import dump, load

from cluequiz.serial import Serial
from cluequiz.screen import Screen
from cluequiz.helper import GameStateHistory, logger


CONFIG_FILE = 'config.yml'


class Game:
    def __init__(self, save):
        self.history = []
        self.config = {}
        with open(CONFIG_FILE, 'r') as f:
            self.config = load(f)
        self.clue_sets = self.get_config('clue-sets')
        if len(self.clue_sets) == 0:
            raise ValueError('At least one complete clue set is needed')
        self.next = 0

        self.serial = Serial(self.get_config('serial.port', '/dev/ttyUSB0'), self.get_config('serial.baud', 9600))

        self.state = []
        for i in range(6):
            self.state.append([ None, None, None, None, None ])
        self.sel = None
        self.scores = [ 0, 0, 0, 0 ]
        self.choosing = 0
        self.responding = None
        self.responded = [ False, False, False, False ]

        if save:
            with open(save, 'r') as f:
                s = load(f)
                if len(s['board']) != 6:
                    raise ValueError('Serialized board state must have six columns')
                for r in s['board']:
                    if len(r) != 5:
                        raise ValueError('Serialized board state must have five rows')
                if len(s['scores']) != 4:
                    raise ValueError('There have to be exactly four score values')
                self.state = s['board']
                self.scores = s['scores']
                self.choosing = s['choosing']

        self.screen = Screen(self)
        self.append_history()

    def get_config(self, key, default=None):
        value = self._resolve(key, self.config)
        if value != None:
            return value
        if default != None:
            return default
        raise SystemExit('Required config key is missing')

    def _resolve(self, key, parent):
        i = key.find('.')
        if i == -1:
            if key in parent:
                return parent[key]
            return None

        k = key[:i]
        if k in parent:
            return self._resolve(key[i+1:], parent[k])
        return None

    def next_clue_set(self):
        clues = self.clue_sets[self.next]
        self.next = self.next + 1
        if self.next == len(self.clue_sets):
            self.next = 0
        return clues

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

    def get_state_at(self, x, y):
        return self.state[x][y]

    def ignore_clue(self):
        self.state[self.sel[0]][self.sel[1]] = -1
        self.save_state()

    def finished(self):
        for s in self.state:
            if None in s:
                return False
        return True

    def set_selected(self, x, y):
        self.sel = (x, y)

    def get_selected(self):
        return self.sel

    def correct(self):
        self.state[self.sel[0]][self.sel[1]] = self.responding
        self.scores[self.responding] = self.scores[self.responding] + (self.sel[1]+1) * 100
        self.choosing = self.responding
        self.save_state()

    def wrong(self):
        self.scores[self.responding] = self.scores[self.responding] - (self.sel[1]+1) * 100
        self.save_state()

    def get_score(self, i):
        return self.scores[i]

    def get_choosing(self):
        return self.choosing

    def set_responding(self, i):
        if not self.responded[i]:
            self.responding = i
            self.responded[i] = True
            return True
        return False

    def get_responding(self):
        return self.responding

    def all_responded(self):
        return not (False in self.responded)

    def clear_responded(self):
        self.responded = [ False, False, False, False ]

    def clear(self):
        self.state = []
        for i in range(6):
            self.state.append([ None, None, None, None, None ])
        self.sel = None
        self.scores = [ 0, 0, 0, 0 ]
        self.choosing = 0
        self.responding = None
        self.responded = [ False, False, False, False ]
        self.save_state()

    def save_state(self):
        self.append_history()
        with open('autosave.yml', 'w') as f:
            f.write(dump({
                'board': self.state,
                'scores': self.scores,
                'choosing': self.choosing
            }))

    def append_history(self):
        """Appenend current game state to history."""
        history_entry = GameStateHistory(
            state=deepcopy(self.state),
            scores=deepcopy(self.scores),
            choosing=deepcopy(self.choosing),
            responded=deepcopy(self.responded),
        )
        self.history.append(history_entry)

    def rollback(self, age=1):
        """Restore to the state of an history entry."""
        if len(self.history) >= age:
            index = age * -1
            restore = deepcopy(self.history[index])
            self.history = self.history[0:index] or [self.history[0]]

            logger.warning('Rolling back to %s.', restore)
            self.state, self.scores, self.choosing, self.responded = restore
            self.screen.render_score(player=None, instance=self)

        else:
            logger.warning('Can not rollback that far.')

    def handle(self, event):
        self.screen.handle(event, self)

    def update(self):
        self.serial.keep_alive()
        self.screen.update(self)
